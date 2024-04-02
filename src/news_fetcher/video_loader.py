import os
import torch
import asyncio
import assemblyai as aai
from pytube import YouTube
from transformers import BertTokenizer, BertModel
from src.utils import sources_collection

from src.utils import config

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

aai.settings.api_key = config['assembly-ai']['api-key']

class VideoLoader:
    def __init__(self, videos):
        self.videos = videos
        self.transcriber = aai.Transcriber()
        self.transcription_config = aai.TranscriptionConfig(language_code="pl")
        self.chunk_size = config["chunking"]['chunk-size']
        self.chunk_overlap = config["chunking"]["chunk-overlap"]

    async def load(self):
        tasks = [self.load_video(video) for video in self.videos]
        return await asyncio.gather(*tasks)

    async def load_video(self, video):
        data = []

        url = video['url']
        timestamp = video['ts']
        print(f'Loading video: {url}')

        try:
            print(f"downloading {url}")
            file = await asyncio.to_thread(YouTube(url).streams.first().download)

            print(f'transcribing {url}')
            transcript = await self.transcriber.transcribe(file, self.transcription_config)

            print(f'chunking transcript {url}')
            chunks = self._chunk_transcript(transcript.text)

            print(f'generating chunks embeddings {url}')
            data_to_insert = [{
                'source_url': url,
                'content': chunk,
                'embedding': self._get_chunk_embedding(chunk),
                'timestamp': timestamp
            } for chunk in chunks]

            print(f'inserting to mongo db {url}')
            sources_collection.insert_many(data_to_insert)

            os.remove(file)
        except Exception as e:
            print(f'Error occured while loading video {url}: {e}')

        return data

    def _chunk_transcript(self, text):
        tokens = text.split(' ')
        chunks = []
        while tokens:
            if len(tokens) < self.chunk_overlap:
                break
            chunk = ' '.join(tokens[:self.chunk_size])
            chunks.append(chunk)
            del tokens[:self.chunk_size - self.chunk_overlap]

        return chunks

    def _get_chunk_embedding(self, chunk_text):
        input_ids = torch.tensor([tokenizer.encode(chunk_text, add_special_tokens=True, max_length=512)])

        with torch.no_grad():
            outputs = model(input_ids)
            cls_embedding = outputs[0][:, 0, :]

        return cls_embedding.flatten()

