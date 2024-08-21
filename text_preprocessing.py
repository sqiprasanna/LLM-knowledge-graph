import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os
nltk_data_dir = os.getenv('NLTK_DATA', '/usr/local/nltk_data')
os.makedirs(nltk_data_dir, exist_ok=True)
# Download necessary NLTK data
nltk.download('stopwords', download_dir=nltk_data_dir)
nltk.download('punkt_tab', download_dir=nltk_data_dir)

class TextPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def clean_text(self, text):
        text = re.sub(r'\W', ' ', str(text))
        text = re.sub(r'\s+', ' ', text)
        text = text.lower()
        return text

    def tokenize_text(self, text):
        tokens = word_tokenize(text)
        filtered_words = [word for word in tokens if word not in self.stop_words]
        return ' '.join(filtered_words)

    def preprocess(self, text):
        cleaned_text = self.clean_text(text)
        tokenized_text = self.tokenize_text(cleaned_text)
        return tokenized_text

if __name__ == "__main__":
    pass