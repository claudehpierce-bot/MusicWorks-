"""MusicWorks™ V4 — Claude worker: text generation (blog, captions, press releases, etc.)."""
import os
from .base_worker import BaseWorker, WorkerResult

_TEXT_JOB_TYPES = [
    "blog", "email", "press_release", "church_outreach",
    "post_launch", "reaction",
]

_MOCK_OUTPUTS: dict[str, str] = {
    "blog": """\
# HLANGANA: When Zulu Teaches Us to Gather

*A devotional reflection on Hebrews 10:25 and the African theology of community*

There is a word in Zulu that the English Bible cannot fully contain.

**HLANGANA** (hla-NGA-na) means to gather together — but not simply to occupy the same room.
It means to become one. To converge with purpose. To arrive at the same place from different journeys and recognize each other as the same people.

The writer of Hebrews knew this need:

> "Do not give up meeting together, as some are in the habit of doing, but encouraging one another — and all the more as you see the Day approaching." — Hebrews 10:25 (NIV)

The African Church has always known what Western Christianity is still learning: community is not optional. Gathering is not a preference. *HLANGANA* is a theological mandate.

This song was written for every diaspora Christian who has sat in a church that felt foreign — whose music didn't sound like home, whose language didn't appear in the liturgy, whose heritage was invisible in the worship.

You were always supposed to be here. *HLANGANA* is your invitation.

---

**Stream HLANGANA on all platforms. Download the free devotional guide at [STREAMING_LINK].**
""",

    "email": """\
Subject: A Zulu word changed how I read Hebrews 10:25

Friend,

There is a word I want you to know.

**HLANGANA.**

It's a Zulu word that means to gather — but deeper than any English translation holds. It means to converge from different places and become one. To recognize each other as the same people.

I wrote a song about it. And I wrote it for you — for everyone who has ever sat in a church that felt foreign, or worshipped in a language that wasn't home.

HLANGANA is out now. Stream it wherever you listen to music.

And if you want to go deeper: I wrote a devotional guide to go alongside the song. It's yours free — no email list, no upsell. Just the Word.

[Download the Devotional Guide →]
[Stream HLANGANA →]

In community,
Fire & Flow Gospel
""",

    "press_release": """\
FOR IMMEDIATE RELEASE

**Fire & Flow Gospel Debuts "HLANGANA" — A Song That Recovers the African Theology of Gathering**

*Afro-Gospel artist bridges cultural heritage and scripture in debut Kingdom Words release*

NEW YORK / PORT OF SPAIN — Fire & Flow Gospel, an independent Afro-Gospel / Amapiano Gospel project representing the African and Caribbean diaspora, releases its debut single "HLANGANA" on [RELEASE DATE].

The title takes its name from the Zulu word meaning "to gather together" — a direct linguistic meditation on Hebrews 10:25. The song is the first entry in the Kingdom Words series, an ongoing project that recovers words from African, Caribbean, and global languages that illuminate biblical concepts in ways that English translation cannot fully capture.

"[FOUNDER QUOTE — required before approval]"

HLANGANA is available on all major streaming platforms. A free devotional guide accompanies the release, designed for small groups, churches, and individual study.

**Streaming:** [STREAMING_LINK]
**Devotional Guide:** [DEVOTIONAL_LINK]
**Press contact:** [EMAIL]
""",

    "church_outreach": """\
Subject: A free devotional resource for your congregation — HLANGANA by Fire & Flow Gospel

Dear Pastor / Ministry Leader,

I am writing to share a resource I believe will serve your congregation.

Fire & Flow Gospel has released "HLANGANA," a new Afro-Gospel song built around Hebrews 10:25 and the Zulu theology of gathering. Alongside the music, we have released a free devotional guide designed for small groups, Sunday discussion, or personal study.

The guide includes:
- Word study: HLANGANA in its cultural and biblical context
- Scripture meditation: Hebrews 10:25 with extended commentary
- Discussion questions for small group or family use
- A prayer of gathering

This resource is free, with no strings attached. We serve the Church — not a mailing list.

**Download the Devotional Guide:** [DEVOTIONAL_LINK]
**Stream HLANGANA:** [STREAMING_LINK]

In His service,
Fire & Flow Gospel
""",

    "post_launch": """\
The numbers don't tell the whole story.

But they tell enough of it.

HLANGANA has been streamed, shared, and prayed over across five continents in its first 24 hours.
People are gathering. That's the whole point.

If you haven't listened yet — there's still time.
And if you have — thank you. You are the community this song was written for.

[STREAMING_LINK] 🔗

#HLANGANA #FireAndFlowGospel #AfroGospel #DiasporaWorship
""",

    "reaction": """\
We see your messages. We read every comment. We listen.

The word HLANGANA means to gather — and you've proven that the diaspora Church is ready to gather.

Here are some of the responses from the first 72 hours:

✦ "This sounds like home and church at the same time."
✦ "I played this on repeat during my morning prayer."
✦ "Finally — a song that sounds like *us*."

That is why this song exists.

Thank you. Keep gathering.

[STREAMING_LINK]
""",
}


class ClaudeWorker(BaseWorker):
    key         = "claude"
    name        = "Claude"
    description = "Text generation: blog posts, captions, press releases, email, church outreach"
    icon        = "🧠"
    color       = "#D4A853"
    provider_url = "https://claude.ai"
    supported_types = _TEXT_JOB_TYPES

    @property
    def available(self) -> bool:
        return bool(os.environ.get("ANTHROPIC_API_KEY"))

    def estimate_time(self, job: dict) -> str:
        return "~30 sec" if self.available else "mock — instant"

    def generate(self, job: dict, brand_context: str = "") -> WorkerResult:
        jtype = job.get("job_type", "blog")
        if not self.available:
            return self._mock(jtype, job)
        return self._live(jtype, job, brand_context)

    def _mock(self, jtype: str, job: dict) -> WorkerResult:
        text = _MOCK_OUTPUTS.get(jtype, f"[Mock output for {jtype}]\n\nThis would be generated by Claude using the artist's Brand Brain and the campaign brief.")
        return WorkerResult(success=True, output_text=text, mock=True)

    def _live(self, jtype: str, job: dict, brand_context: str) -> WorkerResult:
        try:
            import anthropic
            client = anthropic.Anthropic()
            prompt = self.build_prompt(job, brand_context)
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            text = message.content[0].text
            return WorkerResult(
                success=True,
                output_text=text,
                prompt_used=prompt,
                tokens_used=message.usage.input_tokens + message.usage.output_tokens,
                mock=False,
            )
        except Exception as e:
            return WorkerResult(success=False, error=str(e))

    def build_prompt(self, job: dict, brand_context: str = "") -> str:
        jtype    = job.get("job_type", "blog")
        title    = job.get("song_title", "")
        phase    = job.get("phase", "launch")
        notes    = job.get("notes", "")
        labels   = {"blog": "blog post", "email": "email newsletter", "press_release": "press release",
                    "church_outreach": "church outreach email", "post_launch": "post-launch social post", "reaction": "reaction/engagement post"}
        label    = labels.get(jtype, jtype)
        ctx_block = f"\n\nBrand Brain context:\n{brand_context[:2000]}" if brand_context else ""
        notes_block = f"\n\nAdditional notes: {notes}" if notes else ""
        return (
            f"You are the AI media writer for Fire & Flow Gospel, an Afro-Gospel / Amapiano Gospel artist."
            f"{ctx_block}\n\n"
            f"Write a {label} for the song '{title}' — phase: {phase}."
            f" Use the brand voice: devotional, scripture-anchored, pastoral, community-focused."
            f" Do not use hype language or pressure tactics."
            f"{notes_block}"
        )
