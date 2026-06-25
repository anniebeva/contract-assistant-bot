import os
from pathlib import Path
from typing import List, Dict

KNOWLEDGE_DIR = "mock_knowledge_base"
STOP_WORDS = {'и', 'в', 'на', 'с', 'по', 'к', 'у', 'за', 'из', 'о', 'об', 'при', 'без', 'до', 'для', 'через', 'около', 'от', 'до', 'про', 'а', 'но', 'или', 'либо', 'да', 'не', 'ни', 'что', 'как', 'так', 'это', 'его', 'её', 'их', 'твой', 'ваш', 'который', 'весь', 'этот', 'тот', 'такой', 'там', 'тут', 'где', 'когда', 'почему', 'зачем', 'кто', 'что'}

def read_files() -> Dict[str, str]:
    files = {}
    for filepath in Path(KNOWLEDGE_DIR).glob("*.md"):
        with open(filepath, 'r', encoding='utf-8') as f:
            files[filepath.name] = f.read()
    return files

def tokenize(text: str) -> set:
    words = text.lower().split()
    clean = []
    for w in words:
        w = w.strip('.,!?;:()[]{}"\'')
        if w and w not in STOP_WORDS:
            clean.append(w)
    return set(clean)

def retrieve_context(query: str, top_k: int = 3) -> List[Dict]:
    query_words = tokenize(query)
    if not query_words:
        return []

    files = read_files()
    candidates = []

    for filename, content in files.items():
        paragraphs = content.split('\n\n')
        for idx, para in enumerate(paragraphs):
            if len(para.strip()) < 20:
                continue
            para_words = tokenize(para)
            overlap = len(query_words & para_words)
            if overlap > 0:
                candidates.append((filename, para.strip(), idx, overlap))

    candidates.sort(key=lambda x: x[3], reverse=True)
    top = candidates[:top_k]

    print(f"[RAG] Запрос: {query}")
    if not top:
        print("[RAG] Ничего не найдено")
    else:
        print(f"[RAG] Найдено {len(top)} фрагментов:")
        for filename, para, idx, score in top:
            print(f"    - {filename} (абзац {idx}, совпадений: {score})")

    return [{"content": para, "metadata": {"source": filename, "chunk_id": idx}} for filename, para, idx, _ in top]