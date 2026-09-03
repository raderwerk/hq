#!/usr/bin/env python3
"""Turn a finished Codex cloud task into a pull request and update the Linear issue.

Usage: codex_task_to_pr.py <codex_task_id> <repo-name> <WV-123> "<PR title>"

Steps: `codex cloud diff` -> git worktree on branch feat/<issue>-codex -> apply --3way ->
commit (co-authored by Codex) -> push -> `gh pr create` -> Linear comment + state Agentreview.
Never merges. Reads the Codex summary from the issue's latest Codex agent session for the PR body.
"""
import os, re, subprocess, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import linear_api  # noqa: E402

ROOT = '/Users/youp/Developer/Personal/Raderwerk'


def sh(cmd, cwd=None, check=True, capture=True):
    r = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), text=True,
                       capture_output=capture)
    if check and r.returncode != 0:
        raise SystemExit(f"command failed ({r.returncode}): {cmd}\n{r.stdout}\n{r.stderr}")
    return (r.stdout or '').strip()


def main():
    task, repo, issue, title = sys.argv[1:5]
    num = int(issue.split('-')[1]); team = issue.split('-')[0]
    gql = linear_api.LinearClient().gql if hasattr(linear_api, 'LinearClient') else linear_api.gql
    diff = sh(f'codex cloud diff {task}')
    if not diff.strip():
        raise SystemExit('empty diff')
    nfiles = diff.count('\ndiff --git ') + (1 if diff.startswith('diff --git') else 0)
    repo_dir = f'{ROOT}/{repo}'
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:40]
    branch = f'feat/{issue.lower()}-{slug}'
    wt = f'{ROOT}/.worktrees/{repo}/{issue}'
    sh('git fetch -q origin', cwd=repo_dir)
    if os.path.exists(wt):
        sh(f'git worktree remove --force {wt}', cwd=repo_dir, check=False)
    os.makedirs(os.path.dirname(wt), exist_ok=True)
    sh(f'git worktree add -q -B {branch} {wt} origin/main', cwd=repo_dir)
    open(f'/tmp/{issue}.diff', 'w').write(diff + '\n')
    sh(f'git apply --3way /tmp/{issue}.diff', cwd=wt)
    # Codex summary from Linear
    r = gql('query($n:Float!,$t:String!){ issues(filter:{number:{eq:$n}, team:{key:{eq:$t}}}){ nodes{ id identifier labels{ nodes{ id name } } agentSessions{ nodes{ createdAt appUser{ name } activities{ nodes{ content{ __typename ... on AgentActivityResponseContent{ body } } } } } } } } }', {'n': num, 't': team})
    iss = (r.get('issues') or r['data']['issues'])['nodes'][0]
    summary = ''
    for s in sorted(iss['agentSessions']['nodes'], key=lambda s: s['createdAt']):
        if s['appUser']['name'] != 'Codex':
            continue
        for a in s['activities']['nodes']:
            b = a['content'].get('body') or ''
            if len(b) > len(summary):
                summary = b
    summary = re.sub(r'\[View task →\]\(<[^>]+>\)', '', summary).strip()
    sh(f'git add -A && git -c commit.gpgsign=false commit -q -m "{title} ({issue})\n\nWork produced by Codex (GPT-5.6 Sol) in its cloud sandbox for Linear issue {issue}, applied from the Codex cloud task diff and opened as a pull request by the orchestrator.\n\nCo-Authored-By: Codex <codex@openai.com>"', cwd=wt)
    sh(f'git push -q -u origin {branch}', cwd=wt)
    body = f"""## Wat
{title}. Linear {issue}.

## Bewijs
Gemaakt door Codex (GPT-5.6 Sol) in de Codex-cloudsandbox (taak {task}); diff ({nfiles} bestanden) opgehaald met `codex cloud diff` en als PR geopend door de orchestrator. Codex' eigen samenvatting:

{summary}

## Poort
Poort · Merge of publicatie: mens keurt en merget na Agentreview en QA. Agents mergen niet.

[Spil / orchestrator]
"""
    open(f'/tmp/{issue}-pr.md', 'w').write(body)
    pr = sh(f'gh pr create -R raderwerk/{repo} --head {branch} --base main --title "{title} ({issue})" --body-file /tmp/{issue}-pr.md', cwd=wt)
    print('PR', pr)
    st = gql('query($t:String!){ workflowStates(filter:{team:{key:{eq:$t}}}){ nodes{ id name } } }', {'t': team})
    states = {s['name']: s['id'] for s in (st.get('workflowStates') or st['data']['workflowStates'])['nodes']}
    lb = gql('query{ issueLabels(first:250){ nodes{ id name parent{ name } } } }', {})
    labels = {((l['parent'] or {}).get('name'), l['name']): l['id'] for l in (lb.get('issueLabels') or lb['data']['issueLabels'])['nodes']}
    ids = {l['id'] for l in iss['labels']['nodes'] if l['name'] not in ('wacht-op-mens', 'onbevestigd', 'bezet')}
    ids.add(labels[('run', 'klaar')])
    gql('mutation($id:String!,$b:String!){ commentCreate(input:{issueId:$id, body:$b}){ success } }',
        {'id': iss['id'], 'b': f"[Spil / orchestrator] Codex-cloudtaak afgerond; diff ({nfiles} bestanden) opgehaald met `codex cloud diff` en als PR geopend: {pr} (branch {branch}). Volgende stap: Agentreview (reviewer + tweede mening), daarna QA op preview, dan de merge-poort."})
    gql('mutation($id:String!,$s:String!,$l:[String!]){ issueUpdate(id:$id, input:{stateId:$s, labelIds:$l}){ success } }',
        {'id': iss['id'], 's': states['Agentreview'], 'l': list(ids)})
    print(f'{issue} -> Agentreview')


if __name__ == '__main__':
    main()
