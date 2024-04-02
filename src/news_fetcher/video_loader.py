import os
import assemblyai as aai
from pytube import YouTube

from src.utils import config

aai.settings.api_key = config['assembly-ai']['api-key']

class VideoLoader:
    def __init__(self, videos):
        self.videos = videos
        self.transcriber = aai.Transcriber()
        self.transcription_config = aai.TranscriptionConfig(language_code="pl")
        self.chunk_size = config["chunking"]['chunk-size']
        self.chunk_overlap = config["chunking"]["chunk-overlap"]

    def load(self):
        data = []
        for video in self.videos:
            url = video['url']
            timestamp = video['ts']
            print(f'Loading video: {url}')

            print("downloading")
            file = YouTube(url).streams.first().download()

            print('transcribing')
            transcript = self.transcriber.transcribe(file, self.transcription_config)

            print('chunking transcript')
            chunks = self._chunk_transcript(transcript.text)
            print(chunks)

            print('generating chunks embeddings')
            for chunk in chunks:
                data.append({
                    'source_url': url,
                    'content': chunk,
                    'embedding': self._get_chunk_embedding(chunk),
                    'timestamp': timestamp
                })
            os.remove(file)

        return data

    def _chunk_transcript(self, text):
        tokens = text.split(' ')
        chunks = []
        while tokens:
            chunk = ' '.join(tokens[:self.chunk_size])
            chunks.append(chunk)
            del tokens[:self.chunk_size - self.chunk_overlap]

        return chunks

    def _get_chunk_embedding(self, chunk_text):
        pass

