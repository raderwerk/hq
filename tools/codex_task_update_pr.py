#!/usr/bin/env python3
"""Apply a finished Codex cloud task (full diff vs main) as a new commit on an EXISTING PR branch.

Usage: codex_task_update_pr.py <codex_task_id> <repo-name> <WV-123> <branch> "<commit title>"
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import linear_api  # noqa: E402
ROOT = '/Users/youp/Developer/Personal/Raderwerk'


def sh(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, shell=True, text=True, capture_output=True)
    if check and r.returncode != 0:
        raise SystemExit(f"command failed ({r.returncode}): {cmd}\n{r.stdout}\n{r.stderr}")
    return (r.stdout or '').strip()


def main():
    task, repo, issue, branch, title = sys.argv[1:6]
    repo_dir = f'{ROOT}/{repo}'
    diff = sh(f'codex cloud diff {task}')
    if not diff.strip():
        raise SystemExit('empty diff')
    open(f'/tmp/{issue}-update.diff', 'w').write(diff + '\n')
    sh('git fetch -q origin', cwd=repo_dir)
    tmp = f'{ROOT}/.worktrees/{repo}/{issue}-tmp'
    wt = f'{ROOT}/.worktrees/{repo}/{issue}'
    for p in (tmp, wt):
        if os.path.exists(p):
            sh(f'git worktree remove --force {p}', cwd=repo_dir, check=False)
    # tree T2 = main + full diff
    sh(f'git worktree add -q --detach {tmp} origin/main', cwd=repo_dir)
    sh(f'git apply --3way /tmp/{issue}-update.diff', cwd=tmp)
    sh('git add -A && git -c commit.gpgsign=false commit -q -m "tmp"', cwd=tmp)
    t2 = sh('git rev-parse HEAD', cwd=tmp)
    # put T2 on top of the PR branch
    sh(f'git worktree add -q {wt} {branch}', cwd=repo_dir)
    sh(f'git rm -r -q . && git checkout {t2} -- . && git add -A', cwd=wt)
    if not sh('git status --porcelain', cwd=wt):
        print('no changes vs branch'); return
    sh(f'git -c commit.gpgsign=false commit -q -m "{title} ({issue})\n\nReview fixes produced by Codex (GPT-5.6 Sol) in its cloud sandbox, applied from the Codex cloud task diff by the orchestrator.\n\nCo-Authored-By: Codex <codex@openai.com>"', cwd=wt)
    sha = sh('git rev-parse --short HEAD', cwd=wt)
    sh(f'git push -q origin {branch}', cwd=wt)
    sh(f'git worktree remove --force {tmp}', cwd=repo_dir, check=False)
    pr = sh(f'gh pr list -R raderwerk/{repo} --head {branch} --json url --jq ".[0].url"')
    body = f"[Spil / orchestrator] Reviewbevindingen verwerkt door Codex (cloudtaak {task}); toegepast als commit {sha} op {branch}. Reviewer: graag opnieuw beoordelen."
    sh(f'gh pr comment {pr} --body "{body}"')
    gql = linear_api.LinearClient().gql if hasattr(linear_api, 'LinearClient') else linear_api.gql
    num = int(issue.split('-')[1]); team = issue.split('-')[0]
    r = gql('query($n:Float!,$t:String!){ issues(filter:{number:{eq:$n}, team:{key:{eq:$t}}}){ nodes{ id } } }', {'n': num, 't': team})
    iid = (r.get('issues') or r['data']['issues'])['nodes'][0]['id']
    st = gql('query($t:String!){ workflowStates(filter:{team:{key:{eq:$t}}}){ nodes{ id name } } }', {'t': team})
    states = {s['name']: s['id'] for s in (st.get('workflowStates') or st['data']['workflowStates'])['nodes']}
    gql('mutation($id:String!,$b:String!){ commentCreate(input:{issueId:$id, body:$b}){ success } }', {'id': iid, 'b': body + f" PR: {pr}"})
    gql('mutation($id:String!,$s:String!){ issueUpdate(id:$id, input:{stateId:$s}){ success } }', {'id': iid, 's': states['Agentreview']})
    print(f'{issue}: {branch} updated with {sha}, PR {pr}, -> Agentreview')


if __name__ == '__main__':
    main()
