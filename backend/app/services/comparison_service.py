from app.services.search_service import semantic_search
from app.services.transcript_service import extract_video_id
from app.services.metadata_service import extract_basic_metadata

from groq import Groq
from dotenv import load_dotenv

import os


# ---------------------------------
# Environment
# ---------------------------------

load_dotenv(dotenv_path=".env")


# ---------------------------------
# Groq Client
# ---------------------------------

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ---------------------------------
# Compare Videos
# ---------------------------------

def compare_videos(video_url_1, video_url_2, question):

    # ---------------------------------
    # Extract Video IDs
    # ---------------------------------

    video_id_1 = extract_video_id(video_url_1)
    video_id_2 = extract_video_id(video_url_2)

    if not video_id_1 or not video_id_2:
        return {
            "question": question,
            "comparison": "One or both YouTube URLs are invalid.",
            "video_a_metadata": {},
            "video_b_metadata": {},
            "video_1_sources": [],
            "video_2_sources": []
        }


    # ---------------------------------
    # Extract Metadata
    # ---------------------------------

    metadata_a = extract_basic_metadata(video_url_1)
    metadata_b = extract_basic_metadata(video_url_2)


    # ---------------------------------
    # Retrieve Relevant Transcript Chunks
    # ---------------------------------

    results_1 = semantic_search(
        question,
        video_id=video_id_1
    )

    results_2 = semantic_search(
        question,
        video_id=video_id_2
    )


    # ---------------------------------
    # Safely Extract Transcript Context
    # ---------------------------------

    documents_1 = results_1.get("documents", [[]])

    if documents_1 and documents_1[0]:
        context_1 = "\n".join(documents_1[0])
    else:
        context_1 = "No transcript evidence was retrieved for Video A."


    documents_2 = results_2.get("documents", [[]])

    if documents_2 and documents_2[0]:
        context_2 = "\n".join(documents_2[0])
    else:
        context_2 = "No transcript evidence was retrieved for Video B."


    # ---------------------------------
    # Comparison Prompt
    # ---------------------------------

    prompt = f"""
You are an expert creator strategist analyzing two YouTube videos.

Your job is to compare Video A and Video B using ONLY the provided
metadata and transcript evidence.

==================================================
IMPORTANT RULES
==================================================

1. VERIFY THE USER'S CLAIM BEFORE ANSWERING.

2. Never assume that Video A performed better than Video B.

3. Never assume that Video B performed better than Video A.

4. If the user's question contains a false premise, explicitly
   correct the premise before answering.

5. Clearly distinguish between:
   - views
   - likes
   - comments
   - followers/subscribers
   - engagement rate
   - duration
   - upload date

6. Do not confuse views with engagement.

7. Do not invent statistics, facts, metrics, events, or information
   that is not present in the provided data.

8. Use metadata for quantitative comparisons.

9. Use transcript evidence only for qualitative content analysis.

10. Do not claim that one metric caused another metric unless the
    provided evidence actually demonstrates causation.

11. Do not infer metrics that are not provided.

    DO NOT claim anything about:
    - watch time
    - retention
    - click-through rate (CTR)
    - shares
    - impressions
    - traffic sources
    - recommendation algorithm performance

    unless those metrics are explicitly provided.

12. Semantic transcript retrieval returns chunks that are most
    relevant to the user's question.

    These chunks may NOT represent the beginning, middle, or end
    of the video.

    Therefore:

    DO NOT claim that a video has a strong or weak opening hook
    unless the provided transcript evidence clearly contains
    evidence about the opening.

13. DO NOT claim that a video has better or worse retention unless
    actual retention data is explicitly provided.

14. DO NOT claim that subscriber/follower count caused a video's
    view count.

15. DO NOT claim that video duration caused higher or lower
    performance.

16. DO NOT make unsupported claims about:

    - brand reputation
    - audience psychology
    - audience behavior
    - YouTube recommendation algorithm
    - reach
    - virality
    - watch time
    - retention
    - visual quality
    - editing quality
    - thumbnail quality
    - production quality

    unless the provided evidence explicitly supports the claim.

17. A transcript cannot prove the presence or absence of visual
    elements.

    Therefore, DO NOT say:

    "The video has no visuals."

    Instead say:

    "Visual elements cannot be evaluated from the provided
    transcript evidence."

18. A transcript excerpt cannot prove the quality of the complete
    video.

    Do not generalize from a small number of retrieved transcript
    chunks to the entire video unless the evidence supports it.

19. Clearly distinguish FACTS from INFERENCES.

    FACT:
    Information directly supported by the provided metadata or
    transcript evidence.

    INFERENCE:
    A reasonable interpretation based on the available evidence.

20. When making an inference, use phrases such as:

    - "This may suggest..."
    - "A possible explanation is..."
    - "Based on the available evidence..."
    - "This could indicate..."
    - "This is worth testing..."

21. Never guarantee that a recommendation will increase:

    - views
    - likes
    - comments
    - retention
    - engagement
    - virality

    Instead use:

    - "may help"
    - "could improve"
    - "is worth testing"
    - "could be tested"

22. Do not recommend changing tags, SEO, thumbnails, titles,
    promotion, or other external factors as though they are proven
    causes of performance unless the provided evidence supports it.

23. If the available evidence is insufficient to answer something,
    explicitly say:

    "The available metadata and transcript evidence is insufficient
    to determine this."

24. Answer the user's actual question first.

25. Do not automatically assume that the user wants Video A or
    Video B improved.

    Only provide improvement recommendations when:
    - the user explicitly asks for improvements, OR
    - improvements are clearly relevant to the question.

26. When comparing performance, always use the actual numbers
    provided in the metadata.

27. If Video B has more views than Video A, do not describe Video B
    as having fewer views simply because the user's question
    assumes otherwise.

28. If the user's question asks "why" something happened, distinguish
    between:

    WHAT THE DATA SHOWS:
    Directly measurable differences.

    POSSIBLE EXPLANATIONS:
    Reasonable hypotheses that cannot be proven from the available
    data.

29. Do not present hypotheses as established causes.

30. Do not claim that transcript evidence proves anything about
    visuals, thumbnails, editing, production quality, or audience
    retention.

31. When the user asks for "improvements", only recommend changes
    that are supported by the available evidence or clearly label
    them as experiments.
32. Do not describe a metric as evidence of "topic popularity",
    "audience interest", or "audience preference" unless the data
    explicitly supports that conclusion.

33. Do not state general marketing or YouTube advice as though it
    came from the video's data.

    If a recommendation comes from general creator strategy rather
    than the provided evidence, clearly label it as a hypothesis
    or experiment.

==================================================
VIDEO A
==================================================

METADATA:

{metadata_a}

TRANSCRIPT EVIDENCE:

{context_1}


==================================================
VIDEO B
==================================================

METADATA:

{metadata_b}

TRANSCRIPT EVIDENCE:

{context_2}


==================================================
USER QUESTION
==================================================

{question}


==================================================
ANALYSIS INSTRUCTIONS
==================================================

First determine exactly what the user is asking.

Then check whether any factual premise in the question is correct.

If the premise is incorrect:

1. Clearly state that the premise is incorrect.
2. Give the relevant numbers from the metadata.
3. Correct the comparison.
4. Answer the underlying question if the available evidence allows it.

If the premise is correct:

1. Confirm it using the provided evidence.
2. Explain the comparison.
3. Use transcript evidence where relevant.

When discussing performance:

- Use metadata for measurable performance.
- Do not confuse views with engagement rate.
- Do not confuse absolute likes/comments with engagement rate.
- Do not claim causation unless demonstrated by the evidence.

When discussing content:

- Only use the supplied transcript evidence.
- Remember that retrieved transcript chunks may represent only
  portions of the video.
- Do not make claims about the opening unless the evidence contains
  the opening.
- Do not make claims about visuals from transcript text.
- Do not make claims about editing or production quality unless
  explicit evidence is provided.

When giving recommendations:

- Base recommendations on actual weaknesses supported by the data.
- Clearly label suggestions as tests rather than guaranteed solutions.
- Do not invent missing analytics.
- Do not claim that a recommendation will definitely increase
  performance.

If the evidence is insufficient, say so instead of guessing.

==================================================
EXAMPLE OF CORRECT REASONING
==================================================

BAD:
"Video B got more views because its hook was stronger."

GOOD:
"Video B has more views than Video A. The available metadata confirms
this difference, but the available transcript evidence is insufficient
to determine whether the opening hook caused the difference in views."

BAD:
"Video B's long duration is hurting retention."

GOOD:
"Video B is longer than Video A at 538 seconds versus 275 seconds.
However, retention data is not available, so the evidence is
insufficient to determine whether the longer duration affects
retention."

BAD:
"The video has no visual elements."

GOOD:
"Visual elements cannot be evaluated from the provided transcript
evidence."

BAD:
"Changing the tags will increase views."

GOOD:
"Testing different metadata or search-oriented wording could be
considered, but the available evidence does not establish that this
would increase views."

==================================================
RESPONSE FORMAT
==================================================

Use the following structure when relevant:

1. Premise Check

2. Direct Answer

3. Quantitative Comparison

4. Evidence-Based Content Analysis

5. Strengths of Video A

6. Strengths of Video B

7. Weaknesses of Video A

8. Weaknesses of Video B

9. Creator Insights

10. Improvement Suggestions

Do not force sections that are irrelevant to the user's question.

For improvement questions, prioritize:
- specific evidence-supported observations
- practical suggestions
- clearly stated experiments
- limitations of the available data

For comparison questions, prioritize:
- premise verification
- actual metrics
- direct answer
- evidence
- distinction between facts and possible explanations

Keep the answer concise and complete.

Maximum response length: approximately 600 words.

Do not leave sentences unfinished.
Do not repeat the same observation in multiple sections.

For improvement questions, provide at most 5 improvement experiments.

For each experiment use:

- Area
- Observation
- Suggested experiment
- What to measure

Do not claim that the experiment will improve a metric.

Most importantly:

NEVER invent evidence.

NEVER present an inference as a fact.

NEVER claim causation when the available data only shows correlation
or a difference between metrics.
"""


    # ---------------------------------
    # Generate AI Comparison
    # ---------------------------------

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    answer = completion.choices[0].message.content


    # ---------------------------------
    # Return Comparison
    # ---------------------------------

    return {
        "question": question,
        "comparison": answer,

        "video_a_metadata": metadata_a,
        "video_b_metadata": metadata_b,

        "video_1_sources": results_1.get(
            "metadatas",
            [[]]
        )[0],

        "video_2_sources": results_2.get(
            "metadatas",
            [[]]
        )[0]
    }