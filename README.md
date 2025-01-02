# pubmed-text-analysis

This is very rough code for identifying keywords in PubMed abstracts. Collaborations to improve the generaility of the code are welcomed. 

## To download the abstract text files:
1. Open https://pubmed.ncbi.nlm.nih.gov/
2. Type in search terms
3. Set filters, e.g. publication date
4. Save citations to file - be sure to choose Abstract (text) as the format
5. Create file to be used in dashboard

## To run the dashboard:
1. Launch cmd prompt
2. Change directory
3. Type streamlit run TextDashboard.py

## To use the dashboard:
1. Enter the path to your folder containing text files in the box
2. Change any defined keywords and/or custom stopwords

## Notes:
1. To obtain the keyword frequency, keywords have been pre-defined as set1 = "muscle contraction, excitation-contraction coupling, neuromuscular junction, energy metabolism, extracellular matrix, cytoskeleton, inflammation, hypertrophy, atrophy, fibre type" and set2 = "model, code, human, male, female, species, in-vitro, in-vivo, ex-vivo, parameter". These can be modified in the script and/or changed on the dashboard. Additional keywords can be entered.
2. To prevent searching for commonly used words, custom stopwords have been pre-defined as "study, using, based, doi, university, results, used, activity, test, science, method, analysis, institute, institution, department, conclusion, a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0".
3. DataFrame features include: Title, Authors, Author Information, Abstract, DOI, PMID.
4. Duplicates are identified and removed based on DOI.

### Example keyword frequency plot
![image](https://github.com/user-attachments/assets/99dc5713-60ba-43b0-862f-35d1b8f08417)

### Example word cloud
![image](https://github.com/user-attachments/assets/edd6572f-5f5a-4563-a061-a4111fba5f6d)
