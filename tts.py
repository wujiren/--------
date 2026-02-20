from src.tts import process
import os

if __name__ == "__main__":
    base_dir = "dataset/summary"

    files = [f for f in os.listdir(base_dir) if f.endswith(".md")]
    for file_name in files:
        if os.path.exists(f"output/{file_name.replace('.md', '.mp3')}"):
            continue
        with open(f"{base_dir}/{file_name}", "r") as f:
            content = f.read()
        texts = [f"{l}\n\n" for l in content.split("\n") if l.strip()]
        process(
            texts=texts,
            output_dir="output/精品音色-101013-16k",
            output_file_prefix=file_name.replace(".md", ".mp3"),
        )
