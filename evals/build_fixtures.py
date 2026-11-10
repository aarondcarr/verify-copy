#!/usr/bin/env python3
"""Writes the synthetic, hand-labeled fixture set. All text is synthetic (authored for this spike),
not harvested from any client or employer. Labels: should_rewrite = a careful editor would rewrite this
for AI-slop reasons before it goes to a client. Over-correction traps are clean copy that a
ban-list (all adverbs / all em dashes / all passive / Wh- openers) would wrongly flag."""
import json
from pathlib import Path

D = "dev"; H = "holdout"
F = []
def add(split, cat, surface, label, text, notes=""):
    F.append(dict(split=split, category=cat, surface=surface, should_rewrite=label,
                  input=text, notes=notes, synthetic=True,
                  model_hint={"classic": "synthetic-claude5-style", "residual55": "synthetic-opus55-style",
                              "structural": "synthetic-opus55-style", "clean": "synthetic-human",
                              "overcorrection": "synthetic-human"}[cat]))

# ---------------- DEV ----------------
add(D,"classic","slack",True,"Here's the thing — the deploy didn't fail because of the code. It failed because of the pipeline. Let that sink in. Happy to dive deeper if useful!")
add(D,"classic","email",True,"Hi Dana, I hope this email finds you well. I wanted to circle back on our conversation and unpack the next steps as we navigate the migration landscape together. Moving forward, we will lean into a phased approach. Hope this helps!")
add(D,"classic","proposal",True,"Make no mistake: modernizing your data platform is a game-changer. The uncomfortable truth is that legacy ETL is holding you back. In this section we'll walk through why the stakes are high and the implications are significant.")
add(D,"classic","lesson",True,"Let me walk you through the basics of prompt caching. It turns out that caching is honestly one of the most powerful levers you have. Full stop. As we'll see, it really changes everything.")
add(D,"classic","workshop",True,"Welcome! In this section we'll do a deep dive into spec-driven development. The real insight is simple: specs are load-bearing. By the end, you'll be able to navigate the landscape with confidence.")
add(D,"classic","email",True,"Let me be clear: we are genuinely committed to your success. This matters because every week of delay costs you. Let me know if you'd like me to expand on any of these points.")
add(D,"residual55","proposal",True,"Claude Code adoption is more than a tooling change, it's a shift in how your teams plan and review work. This matters for three reasons: speed, quality, and governance. Looking ahead, the program adds another layer of dependable delivery.")
add(D,"residual55","email",True,"Thanks for the call today. Why this matters: your platform team owns the rollout, so their buy-in is the dependable path to adoption. Rather than simply piloting, we recommend a staged plan. What comes next is a scoping session on Tuesday.")
add(D,"residual55","slack",True,"Quick update on the eval harness. This matters because the rewrite path is expensive. The gate is more than a filter, it's a routing layer. Looking ahead, we'll tune thresholds per surface.")
add(D,"residual55","workshop",True,"Why governance matters\n\nGovernance is more than a checklist — it's the steady foundation that keeps agents dependable. This matters most when teams scale. Just as important, it adds another layer of trust for leadership.")
add(D,"residual55","lesson",True,"Hooks are more than scripts, they're guardrails. Rather than simply blocking commands, a good hook explains why. This matters because agents learn from the feedback in stderr. Looking ahead, the next lesson covers Stop hooks.")
add(D,"residual55","proposal",True,"Our approach is dependable, steady, and measurable. Rather than simply delivering a report, we leave a working repo. This matters: clients who finished an implementation six months ago are already behind.")
add(D,"structural","slack",True,"**Summary**\n- Gate threshold: updated\n- Fixtures: added\n- Next steps: review\n\n**Key takeaways**\n- Threshold is better\n- Fixtures are better\n- Review is next","Over-structured one-line update; no lexical tells.")
add(D,"structural","email",True,"You asked whether we can move Thursday's session. To summarize your question: you would like to know if the session can move. Yes, we can move it to Friday at 10. In summary, Friday at 10 works, and we can move the session.","Restates the ask, recaps the answer; no listed phrases.")
add(D,"structural","proposal",True,"## Overview\nThis section provides an overview.\n\n## Approach\nOur approach is outlined below.\n\n## Benefits\nThe benefits are speed, quality, and alignment.\n\n## Conclusion\nIn conclusion, the approach delivers speed, quality, and alignment.","Header scaffolding around no content.")
add(D,"structural","workshop",True,"Agenda: Discover, Design, Deliver. In Discover we explore. In Design we define. In Deliver we drive. Each phase builds alignment, momentum, and clarity across stakeholders, leaders, and teams.","Padded triads, no listed phrases.")
add(D,"clean","email",False,"Dana, attached is the revised SOW. Two changes from Friday: the discovery phase is now three weeks instead of four, and we moved the security review ahead of the pilot. Total stays at $148,000. Can you get legal comments back by the 18th?")
add(D,"clean","slack",False,"pushed the new fixtures to the eval branch. 3 of them fail the gate on purpose, see notes field. I'll rerun after lunch")
add(D,"clean","proposal",False,"Phase 1 stands up SSO, audit logging, and usage dashboards for 400 engineers across two AWS accounts. We will configure managed settings centrally and hand the policy repo to your platform team at the end of week two. Phase 2 starts only after your security team signs off on the logging design.")
add(D,"clean","lesson",False,"A PreToolUse hook runs before Claude calls a tool. If the script exits with code 2, the call is blocked and whatever the script wrote to stderr goes back to the model. Write that message for the model: say what was blocked and what to do instead.")
add(D,"clean","workshop",False,"Bring one real ticket from your backlog. We will write a spec for it together in the first hour, run it through Claude Code in the second, and spend the last thirty minutes reviewing the diff line by line. Laptops need repo access before the session.")
add(D,"clean","email",False,"Thanks for the quick turnaround on the access request. Two engineers still can't see the staging bucket: Priya and Marco. Their IAM users are in the ticket. Once they're in, we can start the load test Wednesday.")
add(D,"clean","slack",False,"heads up, Sonnet 5.5 broke our thinking-off config. you need between_tools now. fix is one line in the agent config, PR is up")
add(D,"clean","proposal",False,"We estimate 6 to 8 weeks for the migration. The range depends on how many of the 37 Glue jobs use custom JARs; we found 9 in the sample you shared and have not reviewed the rest. We will confirm the estimate by the end of week one.")
add(D,"clean","email",False,"Sam, the design review is set for Thursday at 8:00 AM CT. I'll bring a one-page brief and the eval results. If 45 minutes runs short, I'd rather cover the gate design than the fixture details.")
add(D,"clean","lesson",False,"Prompt caching charges a write premium the first time a prefix is stored and a much smaller read price after that. For a system prompt you reuse hundreds of times an hour, the read price dominates. For a one-off request, caching costs more than it saves.")
add(D,"overcorrection","proposal",False,"The pilot actually finished a week early — the client's platform team had already automated account vending, which we had budgeted two weeks to build. We are reallocating that time to the evaluation harness.","Legit 'actually' (correcting expectation) and one em dash.")
add(D,"overcorrection","email",False,"I really appreciate you making time on short notice. The board deck is attached; slides 4 and 9 are the ones I'd most like your read on before Friday.","One sincere 'really'. Ban-all-adverbs would flag.")
add(D,"overcorrection","lesson",False,"The prompt was rewritten by the reviewer, and the eval scores were recomputed overnight. What changed is the ordering of examples: the failing cases now come first.","Passive voice and a Wh- opener that are fine.")
add(D,"overcorrection","proposal",False,"This is not a lift-and-shift. Your contract with the current vendor requires re-platforming the scheduler, so we priced the work as a rebuild of 14 workflows, not a copy.","'Not X' corrects a real misconception the client stated; stays.")
add(D,"overcorrection","workshop",False,"When should you write a skill instead of a CLAUDE.md rule? When the instructions are long, only matter for one kind of task, and would waste context the rest of the time. Otherwise, use the rule.","Wh- openers and a rhetorical question that is the actual topic.")
add(D,"overcorrection","slack",False,"honestly no idea why the cache hit rate dropped — checking the prefix now","Casual 'honestly' and em dash in Slack.")
add(D,"overcorrection","email",False,"The client said, \"Here's the thing: we just need it to work by March.\" I think we should take that literally and cut scope to the two workflows finance uses daily.","Hard tell inside a quotation. Gate should not rewrite a quote.")
add(D,"overcorrection","proposal",False,"Each agent run is logged with the prompt, the tool calls, and the final diff. Reviews are assigned automatically to the code owner, and nothing merges without a human approval — that rule is enforced in branch protection, not in the agent.","Passive voice, em dash, and a 'not X' that is precise.")

# ---------------- HOLDOUT (written before v2 heuristic results were inspected on it) ----------------
add(H,"classic","email",True,"I hope you're doing well! I just wanted to quickly circle back and touch base regarding the proposal. Here's what I think: it's honestly a game-changer for your team. Let me know if you'd like me to dive deeper!")
add(H,"classic","proposal",True,"The real question is not whether to adopt AI, it's how fast. Make no mistake, the landscape is shifting. Let that sink in. Our team will help you navigate it and lean into the opportunity.")
add(H,"classic","slack",True,"ok so here's the thing — the rollback literally saved us. not the alerting. the rollback. full stop.")
add(H,"classic","lesson",True,"In this section we'll unpack evaluation. It turns out evals are simply the most important part of any AI system. As we'll see, they're crucially load-bearing.")
add(H,"classic","workshop",True,"Let me walk you through today. The uncomfortable truth is most teams genuinely struggle with agents. This matters because the gap is growing. Hope this helps set the stage!")
add(H,"classic","email",True,"Thanks so much for your time today! I really wanted to say that this partnership is truly exciting. Moving forward, we'll do a deep dive into your architecture. Happy to dive deeper on anything.")
add(H,"residual55","proposal",True,"Spec-driven development is more than a process, it's a way of working. Rather than simply generating code, teams align on intent first. This matters because rework is the largest hidden cost. Looking ahead, we'll extend the pattern to testing.")
add(H,"residual55","email",True,"Following up on Tuesday. Why the timeline matters: your fiscal year closes in March. Our plan is steady and dependable. What comes next is a joint review of the backlog.")
add(H,"residual55","slack",True,"This matters: the hook is more than a check, it's a cost control. adds another layer of safety too. looking ahead, haiku might do the gate.")
add(H,"residual55","workshop",True,"Why evals matter\n\nAn eval set is more than a test suite — it's institutional memory. Just as important, it gives the team a dependable signal. This matters most after a model upgrade.")
add(H,"residual55","lesson",True,"Context is more than tokens, it's attention. This matters because every line in CLAUDE.md competes for it. Rather than simply adding rules, prune the ones that no longer fire.")
add(H,"residual55","proposal",True,"Our delivery model is dependable and steady. Looking ahead, the platform adds another layer of governance. What comes next: a two-week Foundation Catalyst.")
add(H,"structural","slack",True,"**Status:** done\n**Blockers:** none\n**Next:** none\n\n**Summary:** The task is done and there are no blockers or next steps.","Over-structured and recapped; no lexical tells.")
add(H,"structural","email",True,"To answer your question about pricing: you asked about pricing. Our pricing is fixed-fee. To recap, pricing is fixed-fee, which answers your question about pricing.","Restate/recap loop.")
add(H,"structural","proposal",True,"## Vision\nA better future.\n\n## Mission\nDeliver better outcomes.\n\n## Values\nInnovation, collaboration, and excellence.\n\n## Summary\nVision, mission, and values aligned for innovation, collaboration, and excellence.","Empty scaffolding and padded triad.")
add(H,"structural","workshop",True,"We will learn, build, and grow. Learning drives building. Building drives growth. Growth drives learning. Together these create a cycle of learning, building, and growth.","Metronomic triad loop.")
add(H,"clean","email",False,"Hi Marcus, the load test finished overnight. p95 latency was 410 ms at 2,000 requests per second, up from 380 ms last week. The regression lines up with the logging change on the 3rd. I'd like to revert it Thursday unless your team needs that log field.")
add(H,"clean","slack",False,"can someone with prod access check if the nightly batch ran? dashboard shows nothing since 2am")
add(H,"clean","proposal",False,"We will deliver three things: a Claude Code managed-settings policy for your 1,200 developers, a hook library that blocks writes outside approved paths, and a usage report your finance team can reconcile against the AWS invoice each month.")
add(H,"clean","lesson",False,"Batch requests cost half the normal price but can take up to 24 hours. Use them for nightly evals and backfills. Do not use them for anything a person is waiting on.")
add(H,"clean","workshop",False,"Before Thursday, install the CLI and run the login command once. If it asks for an organization, pick the one ending in -labs. We lose fifteen minutes every session to setup, and I'd rather spend them on your code.")
add(H,"clean","email",False,"Sarah, I can't make the 3:00. Could we do 4:30, or tomorrow morning before 10? I've read the draft; my only real question is the data retention clause in section 6.")
add(H,"clean","slack",False,"merged. reverted the threshold to 0.35 since 0.4 flagged half the clean emails")
add(H,"clean","proposal",False,"Our estimate assumes your team provides one platform engineer for 50% of their time during weeks 2 through 5. If that person is not available, the schedule slips by roughly the same number of weeks, and we will tell you as soon as we see it.")
add(H,"clean","lesson",False,"Skills load their full instructions only when Claude decides they apply. The name and description are always in context, so keep those short and specific. Put long reference material in separate files the skill links to.")
add(H,"clean","email",False,"Attached are the before-and-after drafts from last week. Of the 40 we ran through the gate, 6 were rewritten. I flagged two where the rewrite dropped a date; those need a human look before we trust the numbers.")
add(H,"overcorrection","proposal",False,"Migration risk is concentrated in one place — the billing service, which still writes to the legacy database directly. Everything else already goes through the API.","Single precise em dash.")
add(H,"overcorrection","email",False,"Just confirming: we're still on for 2 PM tomorrow? I'll send the dial-in an hour before.","Plain 'just'.")
add(H,"overcorrection","slack",False,"really nice catch on the cache prefix bug — that would've cost us","Sincere praise, em dash, adverb.")
add(H,"overcorrection","lesson",False,"Why does the model ignore a rule buried on line 400 of CLAUDE.md? Attention is finite, and instructions placed far from the task get less of it. That is the practical case for short contracts.","Wh- opener is the lesson's actual question.")
add(H,"overcorrection","proposal",False,"The integration is not real-time. Orders sync every fifteen minutes, which the client confirmed is acceptable for the warehouse use case.","Precise negation stating a real limitation.")
add(H,"overcorrection","email",False,"Your note said, \"Let me be clear, we will not extend the deadline.\" Understood. We will ship the reduced scope on the 30th and move reporting to phase two.","Hard tell inside quoted client text.")
add(H,"overcorrection","workshop",False,"The repo was forked from the baseline last month, so some skills are out of date. Run the update command first. What you'll see is a diff of every rule that changed since the fork.","Passive voice and Wh- opener, both fine.")
add(H,"overcorrection","proposal",False,"We actually recommend against fine-tuning here. The 300 labeled tickets you have are enough to evaluate a prompted model but not to train one, and a prompted model can be swapped when a better one ships.","'Actually' marks a real disagreement with the client's ask.")

root = Path(__file__).parent / "fixtures"
for split in (D, H):
    for cat in sorted({f["category"] for f in F if f["split"] == split}):
        items = [f for f in F if f["split"] == split and f["category"] == cat]
        for i, it in enumerate(items, 1):
            it["id"] = f"{split}-{cat}-{i:02d}"
        (root / split / f"{cat}.json").write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n")
print(len(F), "fixtures written")
