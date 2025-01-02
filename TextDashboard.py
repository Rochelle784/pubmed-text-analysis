#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 02 11:48 2025

@author: rochelletaylor
"""

import streamlit as st
import os
import pandas as pd
import re
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob, Word
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
nltk.download('wordnet')

# Function to extract information from text and convert to DataFrame
def process_text_to_df(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    entries = []
    entry = {"Title": "", "Authors": "", "Author Information": "", "Abstract": "", "DOI": "", "PMID": ""}
    is_abstract = False
    is_author_info = False
    title_extracted = False
    authors_extracted = False
    blank_line_after_title = False
    doi_found = False

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    for line in lines:
        line = line.strip()
        if re.match(r'^\d+\.\s', line):
            if entry["Title"]:
                entries.append(entry)
                entry = {"Title": "", "Authors": "", "Author Information": "", "Abstract": "", "DOI": "", "PMID": ""}
            title_extracted = False
            authors_extracted = False
            is_abstract = False
            is_author_info = False
            blank_line_after_title = False
            doi_found = False
        elif not title_extracted and line and not line.lower().startswith("10.1") and not any(line.startswith(month) for month in months) and not line.startswith('Epub') and not line.startswith('eCollection') and not line[0].isdigit():
            entry["Title"] = line
            title_extracted = True
            blank_line_after_title = True
        elif title_extracted and blank_line_after_title and not line:
            blank_line_after_title = False
        elif title_extracted and blank_line_after_title and (":" in entry["Title"] or line):
            entry["Title"] += " " + line
        elif title_extracted and not authors_extracted and line:
            entry["Authors"] = line
            authors_extracted = True
        elif "Author information:" in line:
            is_author_info = True
        elif is_author_info:
            if line:
                entry["Author Information"] += line + " "
            else:
                is_author_info = False
        elif line.lower().startswith("doi:"):
            entry["DOI"] = re.findall(r'\d+\.\d+/[^\s]+', line)[0] if re.findall(r'\d+\.\d+/[^\s]+', line) else ""
            doi_found = True
        elif "PMID:" in line:
            entry["PMID"] = line.replace("PMID:", "").replace("[Indexed for MEDLINE]", "").strip()
        elif authors_extracted and re.match(r'^[A-Z]', line) and len(line.split()) > 8:
            is_abstract = True
            entry["Abstract"] += line + " "
        elif is_abstract:
            if line:
                entry["Abstract"] += line + " "
            else:
                is_abstract = False

    if entry["Title"]:
        entries.append(entry)

    return pd.DataFrame(entries)

# User input for folder path
folder_path = st.text_input("Enter the path to your folder containing text files:", "")

if folder_path and os.path.exists(folder_path):
    # Get a list of all text files in the folder
    txt_file_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.txt')]

    if txt_file_list:
        # Generate corresponding CSV filenames
        csv_file_list = [f.replace('.txt', '.csv') for f in txt_file_list]

        # Process each text file and save as CSV
        dataframes = []
        for txt_file, csv_file in zip(txt_file_list, csv_file_list):
            df = process_text_to_df(txt_file)
            df.to_csv(csv_file, index=False)
            dataframes.append(df)

        # Combine all dataframes
        combined_df = pd.concat(dataframes)
        rows_before = combined_df.shape[0]
        combined_df.drop_duplicates(subset='DOI', inplace=True)
        rows_after = combined_df.shape[0]
        rows_removed = rows_before - rows_after

        st.write(f"Number of rows before removing duplicates: {rows_before}")
        st.write(f"Number of rows after removing duplicates: {rows_after}")
        st.write(f"Number of rows removed: {rows_removed}")

        st.write(combined_df.head())

        # Function to extract defined keywords and their frequencies from text
        def extract_defined_keywords_with_frequencies(text, defined_keywords):
            words = text.lower().split()
            words = [word for word in words if word in defined_keywords]
            keywords_with_frequencies = Counter(words).most_common()
            return keywords_with_frequencies

        # Function to process a combined DataFrame and plot defined keyword frequencies
        def process_combined_df_and_plot(combined_df, defined_keywords):
            combined_text = " ".join(combined_df['Abstract'].dropna().tolist())
            keywords_with_frequencies = extract_defined_keywords_with_frequencies(combined_text, defined_keywords)
            st.write(f"Defined keywords and their frequencies: {keywords_with_frequencies}")
            if keywords_with_frequencies:
                keywords, frequencies = zip(*keywords_with_frequencies)
                plt.figure(figsize=(10, 6))
                plt.bar(keywords, frequencies, color='skyblue')
                plt.xlabel('Keywords')
                plt.ylabel('Frequency')
                plt.title('Defined Keyword Frequency')
                plt.xticks(rotation=45)
                st.pyplot(plt)
                
        # Get user-defined keywords 
        user_defined_keywords_set1 = st.text_input("Enter defined keywords (comma-separated):", "muscle contraction, excitation-contraction coupling, neuromuscular junction, energy metabolism, extracellular matrix, cytoskeleton, inflammation, hypertrophy, atrophy, fibre type")
        # Convert the user input to a set of keywords
        defined_keywords_set1 = set(map(str.strip, user_defined_keywords_set1.split(',')))
        # Process and plot the combined DataFrame with user-defined keywords
        process_combined_df_and_plot(combined_df, defined_keywords_set1)

        # Display user-defined keywords 
        user_defined_keywords_set2 = st.text_input("Enter defined keywords (comma-separated):", "model, code, human, male, female, species, in-vitro, in-vivo, ex-vivo, parameter")
        # Convert the user input to a set of keywords
        defined_keywords_set2 = set(map(str.strip, user_defined_keywords_set2.split(',')))
        # Process and plot the combined DataFrame with user-defined keywords
        process_combined_df_and_plot(combined_df, defined_keywords_set2)

        # Function to extract keywords and their frequencies from text with custom stopwords
        def extract_keywords_with_frequencies(text, num_keywords=10, custom_stopwords=None):
            text = re.sub(r'[^\w\s]', '', text).lower()
            words = text.split()
            stop_words = set(stopwords.words('english'))
            if custom_stopwords:
                stop_words.update(custom_stopwords)
            words = [word for word in words if word not in stop_words]
            words = [Word(word).lemmatize() for word in words]
            keywords_with_frequencies = Counter(words).most_common(num_keywords)
            return keywords_with_frequencies

        # Function to process the DataFrame and plot keyword frequencies
        def process_dataframe(df, custom_stopwords=None):
            combined_text = ' '.join(df['Abstract'].dropna().tolist())
            keywords_with_frequencies = extract_keywords_with_frequencies(combined_text, custom_stopwords=custom_stopwords)
            st.write(f"Keywords and their frequencies: {keywords_with_frequencies}")
            keywords, frequencies = zip(*keywords_with_frequencies)

            plt.figure(figsize=(10, 6))
            plt.bar(keywords, frequencies, color='skyblue')
            plt.xlabel('Keywords')
            plt.ylabel('Frequency')
            plt.title('Keyword Frequency')
            plt.xticks(rotation=45)
            st.pyplot(plt)

            text = ' '.join([keyword for keyword, freq in Counter(keywords).items() for _ in range(freq)])
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

            plt.figure(figsize=(10, 6))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Keyword Frequency Word Cloud')
            st.pyplot(plt)

        # Get user-defined stopwords
        custom_stopwords_input = st.text_input(
            "Enter custom stopwords (comma-separated):", 
            "study, using, based, doi, university, results, used, activity, test, science, method, analysis, institute, institution, department, conclusion, a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0"
        )

        # Convert the user input to a set of stopwords
        custom_stopwords = set(map(str.strip, custom_stopwords_input.split(',')))

        # Process the DataFrame with the user-defined stopwords
        process_dataframe(combined_df, custom_stopwords=custom_stopwords)
    else:
        st.write("No text files found in the specified folder.")
else:
    st.write("Please enter a valid folder path to proceed.")