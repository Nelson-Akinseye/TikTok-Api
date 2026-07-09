# All imports
from TikTokApi import TikTokApi
import asyncio
import os
import datetime
import csv
import threading
from transformers import pipeline
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sentence_transformers import SentenceTransformer,util
import emoji
from lingua import Language, LanguageDetectorBuilder
import re

# All transformer model initalizations 
classifier = pipeline("sentiment-analysis", model="j-hartmann/sentiment-roberta-large-english-3-classes")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
namer = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
detector = LanguageDetectorBuilder.from_languages(Language.ENGLISH).build()

# Semantic encodings phrases
meaning0 = "dopamine detox"
meaning1 = "breaking phone addiction"
meaning2 = "improving focus"
meaning3 = "building better habits"
meaning4 = "stress relief"
meaning5 = "feeling more productive"
meaning6 = "better mental health"
meaning7 = "self improvement"
meaning8 = "useful information"

query_embedding0 = semantic_model.encode(meaning0, convert_to_tensor=True)
query_embedding1 = semantic_model.encode(meaning1, convert_to_tensor=True)
query_embedding2 = semantic_model.encode(meaning2, convert_to_tensor=True)
query_embedding3 = semantic_model.encode(meaning3, convert_to_tensor=True)
query_embedding4 = semantic_model.encode(meaning4, convert_to_tensor=True)
query_embedding5 = semantic_model.encode(meaning5, convert_to_tensor=True)
query_embedding6 = semantic_model.encode(meaning6, convert_to_tensor=True)
query_embedding7 = semantic_model.encode(meaning7, convert_to_tensor=True)
query_embedding8 = semantic_model.encode(meaning8, convert_to_tensor=True)

dictQuery = {0:query_embedding0,1:query_embedding1,2:query_embedding2,3:query_embedding3,4:query_embedding4,5:query_embedding5,6:query_embedding6,7:query_embedding7,8:query_embedding8}

def allEmojiOrOtherLanguage(text):
    clean_text = text.replace(" ", "")
    if not clean_text:
        return True
    return all(emoji.is_emoji(char) for char in clean_text) or not (detector.detect_language_of(text) == Language.ENGLISH) or text == "[Sticker]"


def cleanseText(listofComments):
    newSetofComments = set()
    phrase_embeddings = semantic_model.encode(listofComments, convert_to_tensor=True)
    for i in range(9):
        similarity_scores = util.cos_sim(dictQuery[i], phrase_embeddings)[0]
        for j,score in enumerate(similarity_scores):
            if allEmojiOrOtherLanguage(listofComments[j]):
                continue
            if listofComments[j] in newSetofComments:
                continue
            if score > 0.30:
                newSetofComments.add(listofComments[j])
    return newSetofComments

# General Initializations
video_id = ""
ms_token = os.environ.get("ms_token",None)
VideoIDList = []
dictionary = {}
# List of strings
rawComments = []
inputFile = input("Type File Name: ")

with open(inputFile,"r") as f:
    for i in f:
        vidID = re.search(r'\d{19}',i)
        if vidID:
            VideoIDList.append(vidID.group())


def addComments(dict,videoID):
    if not dict[videoID]:
        return
    SetofComments = cleanseText(dict[videoID])
    for comment in SetofComments:
        rawComments.append(comment)


def sentiment(string):
    results = classifier(string,top_k=None)
    return f":: {results[0]["label"]}={results[0]["score"] * 100:.2f}, {results[1]["label"]}={results[1]["score"] * 100:.2f}, {results[2]["label"]}={results[2]["score"] * 100:.2f}"

async def SearchTerm():
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=3,
            browser=os.getenv("TIKTOK_BROWSER", "firefox"),
            headless=False
        )
        for video in VideoIDList:
            try:
                async for comment in api.video(video).comments(500):
                    dataC = comment.as_dict
                    if video not in dictionary:
                        dictionary[video] = [dataC.get("text")]
                    else:
                        dictionary[video].append(dataC.get("text"))
                thread = threading.Thread(target=addComments, args=(dictionary,video))
                thread.start()
            except: 
                pass
    thread.join()
    num_clusters = 9
    if rawComments:
        embeddings = semantic_model.encode(rawComments)
        kmeans = KMeans(n_clusters=9, random_state=42)
        kmeans.fit(embeddings)

        cluster_comments = {i: [] for i in range(num_clusters)}
        for text, label in zip(rawComments, kmeans.labels_):
            cluster_comments[label].append(text)
        with open("commentGroups(f).txt", "w", encoding="utf-8") as files:
            for cluster in range(num_clusters):
                comments = cluster_comments[cluster]
                if len(comments) == 0:
                    continue
                sample = "\n".join(comments[:20])
                prompt = f"""You are naming a cluster of TikTok comments.Give ONLY a short topic name (2-10 words). Comments:{sample} Topic:"""
                cluster_name = namer(prompt,max_new_tokens=8,do_sample=False)[0]["generated_text"]
                cluster_name = cluster_name.split("Topic:")[-1].strip().split("\n")[0]
                vectorizer = TfidfVectorizer(stop_words="english",max_features=5)
                tfidf_matrix = vectorizer.fit_transform(comments)
                feature_names = vectorizer.get_feature_names_out()
                scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
                top_indices = scores.argsort()[::-1]
                keywords = [feature_names[i] for i in top_indices]
                files.write("\n")
                files.write(f"[[** Group {cluster} **]]: {cluster_name}\n")
                files.write(f"Keywords: {', '.join(keywords)}\n\n")
                for comment in comments:
                    files.write(f"{comment} {sentiment(comment)}\n")
                files.write("\n")
    else:
        print("None Found")
            
if __name__ == "__main__":
    asyncio.run(SearchTerm())
