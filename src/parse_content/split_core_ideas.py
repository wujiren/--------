import os
import re
import textwrap


def sanitize_filename(name):
    # Replace colons with dashes for the filename
    name = name.replace(":", "——").replace("：", "——")
    # Remove characters that are generally problematic in filenames
    name = re.sub(r'[\\/*?"<>|？。，！!]', "_", name)
    # Remove formatting like **
    name = name.replace("*", "")
    return name.strip()


def split_core_ideas(source_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Regex to find the start of a card
    card_start_pattern = re.compile(r"^## 核心思想卡\d+.*", re.MULTILINE)

    for filename in sorted(os.listdir(source_dir)):
        if not filename.endswith(".md"):
            continue

        file_path = os.path.join(source_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find all starts of cards
        matches = list(card_start_pattern.finditer(content))
        if not matches:
            continue

        extracted_ranges = []
        name_parts = filename.split(".", 1)
        prefix = (
            name_parts[0] if len(name_parts) == 2 else os.path.splitext(filename)[0]
        )
        chapter_name = os.path.splitext(filename)[0]

        for i, match in enumerate(matches, 1):
            start = match.start()
            next_start = matches[i].start() if i < len(matches) else len(content)
            block = content[start:next_start]

            # --- Fine-grained parsing ---

            # 1. Title (###)
            title_match = re.search(r"^###\s*(.*?)(?:\n|\Z)", block, re.MULTILINE)
            if not title_match:
                print(
                    f"Warning: No title (###) found in card block in {filename} at pos {start}"
                )
                continue

            raw_title = title_match.group(1).strip().strip("*")
            title = re.sub(r"^(核心命题|核心思想)[：:]\s*", "", raw_title)

            # 2. Sections
            required_fields = ["思辨点", "内容分析", "思辨结论", "金句"]
            sections = {}
            missing_fields = []
            last_field_end_in_block = 0

            for field in required_fields:
                field_pattern = rf"^- \*\*({field})\*\*：(.*?)(?=\n- \*\*|\n##|\n#|\Z)"
                f_match = re.search(field_pattern, block, re.DOTALL | re.MULTILINE)

                if f_match:
                    sections[field] = f_match.group(2)
                    # We track the end of the last required field to know what to remove from original
                    last_field_end_in_block = f_match.end()
                else:
                    missing_fields.append(field)

            if missing_fields:
                print(
                    f"Warning: Card '{title}' in {filename} is missing fields: {', '.join(missing_fields)}"
                )
                continue

            # 3. Clean Reconstructed Content
            display_title = title.replace("——", "：").replace("——", "：")

            # Building the final string
            output_lines = [
                f"### {display_title}",
                "",
                f"- **思辨点**：{sections['思辨点'].strip()}",
                "",
            ]

            analysis_clean = textwrap.dedent(sections["内容分析"]).strip()
            if "\n" in analysis_clean:
                indented_analysis = textwrap.indent(analysis_clean, "  ")
                output_lines.append(f"- **内容分析**：\n{indented_analysis}")
            else:
                output_lines.append(f"- **内容分析**：{analysis_clean}")
            output_lines.append("")

            output_lines.append(f"- **思辨结论**：{sections['思辨结论'].strip()}")
            output_lines.append("")
            output_lines.append(f"- **金句**：{sections['金句'].strip()}")
            output_lines.append("")
            output_lines.append("### 参考资料 ：")
            output_lines.append("")
            output_lines.append(f"- 西方现代思想讲义(刘擎)：{chapter_name}")
            output_lines.append("")

            final_content = "\n".join(output_lines)

            # 4. Filename & Save
            safe_title = sanitize_filename(title)
            new_filename = f"{safe_title}.md" if safe_title else f"{prefix}-{i}.md"
            dest_path = os.path.join(dest_dir, new_filename)

            if os.path.exists(dest_path):
                new_filename = f"{prefix}-{new_filename}"
                dest_path = os.path.join(dest_dir, new_filename)

            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(final_content)

            extracted_ranges.append((start, start + last_field_end_in_block))

        # Update original file
        new_original_content = content
        for r_start, r_end in sorted(
            extracted_ranges, key=lambda x: x[0], reverse=True
        ):
            new_original_content = (
                new_original_content[:r_start] + new_original_content[r_end:]
            )

        new_original_content = re.sub(r"\n{3,}", "\n\n", new_original_content).strip()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_original_content)

        if extracted_ranges:
            print(f"Processed {len(extracted_ranges)} cards from {filename}")


if __name__ == "__main__":
    source = "dataset/philosophical_proposition/核心思想提炼"
    dest = "dataset/philosophical_proposition/核心思想卡"
    split_core_ideas(source, dest)

    for file_name in os.listdir(source):
        with open(os.path.join(source, file_name), "r", encoding="utf-8") as f:
            content = f.read()
            if content.strip():
                print(content)
