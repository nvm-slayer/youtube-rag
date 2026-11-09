
import time

from groq import Groq
from youtube_rag.config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)


def generate_summary(prompt):
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an educational content summarizer. "
                    "Be accurate, concise and beginner-friendly. "
                    "Include important concepts and explanations. "
                    "Do not invent information. Keep the summary "
                    "to approximately 150 words."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content


def summarize_video(video_title, chunks):
    batch_size = 5
    batch_summaries = []

    # Step 1: Summarize smaller batches
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]

        transcript = "\n".join(
            chunk["text"] for chunk in batch
        )

        print(f"Summarizing batch {i // batch_size + 1}...")

        summary = generate_summary(
            f"Summarize this part of the video '{video_title}':\n\n"
            f"{transcript}"
        )

        batch_summaries.append(summary)

        # Stay within the current TPM limit
        if i + batch_size < len(chunks):
            time.sleep(15)

   
    # Step 2: Combine batch summaries in smaller groups
    group_size = 5
    group_summaries = []

    for i in range(0, len(batch_summaries), group_size):
        group = batch_summaries[i:i + group_size]

        combined = "\n\n".join(group)

        print(f"Combining group {i // group_size + 1}...")

        group_summary = generate_summary(
            f"Combine these partial summaries of '{video_title}' "
            f"into one concise summary. Preserve important concepts "
            f"and remove repetition:\n\n{combined}"
        )

        group_summaries.append(group_summary)

        if i + group_size < len(batch_summaries):
            time.sleep(15)

    # Step 3: Generate final video summary
    combined_groups = "\n\n".join(group_summaries)

    print("Generating final video summary...")

    final_summary = generate_summary(
        f"Create a coherent final summary of '{video_title}' "
        f"from these grouped summaries. Include the main topic, "
        f"key concepts and important takeaways:\n\n{combined_groups}"
    )

    return final_summary
def summarize_playlist(video_summaries):
    summaries = "\n\n".join(
        f"Video: {item['title']}\n{item['summary']}"
        for item in video_summaries
    )

    return generate_summary(
        "Create an overall course summary using these "
        "individual video summaries. Explain the learning "
        "sequence, major topics and key takeaways:\n\n"
        f"{summaries}"
    )