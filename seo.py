import tkinter as tk
import webbrowser
from autocorrect import Speller
import time
import requests
import math

class TrieNode:
    def __init__(self):
        self.is_end_word = False
        self.child_nodes = {}

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.spell = Speller(lang='en')
        self.autocorrect_dict = {'bg': 'bigg', 'bss': 'boss'}  # Add more entries as needed

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.child_nodes:
                node.child_nodes[char] = TrieNode()
            node = node.child_nodes[char]
        node.is_end_word = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.child_nodes:
                return False
            node = node.child_nodes[char]
        return node.is_end_word

    def suggestions_recursive(self, node, prefix, suggestions):
        if node.is_end_word:
            suggestions.append(prefix)

        for char, child_node in node.child_nodes.items():
            self.suggestions_recursive(child_node, prefix + char, suggestions)

    def spell_check(self, word):
        if word in self.autocorrect_dict:
            return [self.autocorrect_dict[word]]
        else:
            suggestions = self.spell(word)
            return [suggestion for suggestion in suggestions if self.search(suggestion)]

    def search_keyword(self, query, grp):
        if self.search(query):
            for k, v in grp.items():
                if query in v:
                    print("Key:", k)
                    return k
        else:
            suggestions = self.spell_check(query)
            if suggestions:
                print("Suggestions:", suggestions)
                return

class HashMap:
    def __init__(self):
        self.map = {}

    def set(self, key, value):
        self.map[key] = value

    def get(self, key):
        return self.map.get(key, [])

    def remove(self, key):
        if key in self.map:
            del self.map[key]

def search_web(query, api_key, custom_search_engine_id, count=7):
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": custom_search_engine_id,
        "q": query,
        "num": count,
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if "items" in data:
        return [result["link"] for result in data["items"]]
    else:
        return []

class SEOToolApp:
    def __init__(self, root, google_api_key, custom_search_engine_id):
        self.root = root
        self.root.title("SEO Tool")
        self.root.geometry("600x400")

        self.trie = Trie()
        self.hash_map = HashMap()
        self.google_api_key = google_api_key
        self.custom_search_engine_id = custom_search_engine_id
        self.search_engine_link_opened = False

        self.create_widgets()
        self.populate_index()

    def create_widgets(self):
        keyword_label = tk.Label(self.root, text="Enter a keyword to search:")
        keyword_label.pack()
        self.keyword_entry = tk.Entry(self.root)
        self.keyword_entry.pack()

        search_button = tk.Button(self.root, text="Search", command=self.search_keyword)
        search_button.pack()

        self.result_text = tk.Text(self.root, height=15, width=60)
        self.result_text.pack()

    def populate_index(self):
        start_time = time.time()

        keywords_urls = {}
        num_keywords = 10  # You can modify this based on your requirements

        for _ in range(num_keywords):
            keyword = "python"  # You can modify this based on your requirements
            urls = search_web(keyword, self.google_api_key, self.custom_search_engine_id)
            keywords_urls[keyword] = urls

        for keyword, urls in keywords_urls.items():
            self.trie.insert(keyword)
            self.hash_map.set(keyword, urls)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"populate_index elapsed time: {elapsed_time} seconds")

    def search_keyword(self):
        start_time = time.time()

        query = self.keyword_entry.get()
        results = search_web(query, self.google_api_key, self.custom_search_engine_id)

        self.result_text.delete(1.0, tk.END)

        if results:
            self.result_text.insert(tk.END, "Search Results:\n")
            for result in results:
                self.result_text.insert(tk.END, f"- {result}\n")

            if not self.search_engine_link_opened:
                webbrowser.open(f"https://cse.google.com/cse?cx={self.custom_search_engine_id}")
                self.search_engine_link_opened = True
        else:
            suggestion = self.trie.search_keyword(query, self.hash_map.map)
            if suggestion:
                self.result_text.insert(tk.END, f"Did you mean: {suggestion}\n")
            else:
                self.result_text.insert(tk.END, "No results found.")

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"search_keyword elapsed time: {elapsed_time} seconds")

if __name__ == "__main__":
    # Replace with your actual API key and custom search engine ID
    google_api_key = 'AIzaSyDssbjCFmSb_DSuybC-V_eWEluvDhpL12g'
    custom_search_engine_id = 'c4acb41fd2ef54b7a'

    root = tk.Tk()
    app = SEOToolApp(root, google_api_key, custom_search_engine_id)
    root.mainloop()