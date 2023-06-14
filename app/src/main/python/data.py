import tensorflow_hub as hub
from sklearn.neighbors import NearestNeighbors
import numpy as np
import re


class SemanticSearch:

    def __init__(self):
        self.use = hub.load('https://tfhub.dev/google/universal-sentence-encoder/4')
        self.fitted = False

    def fit(self, data, batch=1000, n_neighbors=3):
        self.data = data
        self.embeddings = self.get_text_embedding(data, batch=batch)
        n_neighbors = min(n_neighbors, len(self.embeddings))
        self.nn = NearestNeighbors(n_neighbors=n_neighbors)
        self.nn.fit(self.embeddings)
        self.fitted = True

    def __call__(self, text, return_data=True):
        inp_emb = self.use([text])
        neighbors = self.nn.kneighbors(inp_emb, return_distance=False)[0]

        if return_data:
            return [self.data[i] for i in neighbors]
        else:
            return neighbors

    def get_text_embedding(self, texts, batch=1000):
        embeddings = []
        for i in range(0, len(texts), batch):
            text_batch = texts[i:(i + batch)]
            emb_batch = self.use(text_batch)
            embeddings.append(emb_batch)
        embeddings = np.vstack(embeddings)
        return embeddings


recommender = SemanticSearch()


def load_recommender(text, start_page=1):
    global recommender
    str = preprocess(text)
    chunks = text_to_chunks(str, start_page=start_page)
    recommender.fit(chunks)
    return 'Loaded success'


def text_to_chunks(texts, word_length=1000, start_page=1):
    text_toks = [t.split(' ') for t in texts]
    chunks = []

    for idx, words in enumerate(text_toks):
        for i in range(0, len(words), word_length):
            chunk = words[i:i + word_length]
            if (i + word_length) > len(words) and (len(chunk) < word_length) and (
                    len(text_toks) != (idx + 1)):
                text_toks[idx + 1] = chunk + text_toks[idx + 1]
                continue
            chunk = ' '.join(chunk).strip()
            chunk = f'[{idx + start_page}]' + ' ' + '"' + chunk + '"'
            chunks.append(chunk)
    return chunks


def preprocess(text):
    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    return text


def generate_answer(question):
    topn_chunks = recommender(question)
    prompt = ""
    prompt += 'search results:\n\n'
    for c in topn_chunks:
        prompt += c + '\n\n'

    prompt += "Instructions: Compose a comprehensive reply to the query using the search results given. " \
              "Cite each reference using [number] notation (every result has this number at the beginning). " \
              "Citation should be done at the end of each sentence. If the search results mention multiple subjects " \
              "with the same name, create separate answers for each. Only include information found in the results and " \
              "don't add any additional information. Make sure the answer is correct and don't output false content. " \
              "If the text does not relate to the query, simply state 'Found Nothing'. Ignore outlier " \
              "search results which has nothing to do with the question. Only answer what is asked. The " \
              "answer should be short and concise."

    prompt += f"Query: {question}\nAnswer:"
    return prompt
