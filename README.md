# Exploratory Analysis of Breast Cancer Datasets

**Author:** Danillo Barros de Souza  
**Email:** danillo.dbs16@gmail.com  
**GitHub:** https://github.com/danillodbs16/Breast_Cancer_Analysis  

---

## 📌 Overview
This project explores multiple breast cancer datasets to identify patterns for:
- Tumor classification (benign vs malignant)
- Survival prediction

### Hypotheses
1. Tumor type can be predicted from statistical features  
2. Patient survival can be predicted from available data  

---

[RESENTATION LINK HERE](https://canva.link/myyozjj8d3d73fo)

---

## 📁 Project Structure

```
.
├── img/                # Figures and visualizations used in the report
├── src/                # Source code
│   ├── notebooks/      # Jupyter notebooks for analysis and exploration
│   ├── utils/          # Helper functions and utilities
│   └── data/           # Processed datasets
├── extra/              # Additional outputs (HTML visualizations and dashboard)
│   ├── html/           # Interactive HTML plots and visualizations
│   └── dashboard/      # Exported dashboard files (e.g., Superset)
```

---

## 📊 Datasets

### 1. Breast Cancer Wisconsin (Categorical)
- 699 samples  
- Features scaled from 1–10 (cell characteristics)  
- Target: **Benign / Malignant**

**Cleaning:**
- Handled missing values (`Bare Nuclei`)
- Standardized labels (2→Benign, 4→Malignant)
- Removed unreliable identifiers

---

### 2. Breast Cancer Wisconsin (Diagnostic)
- 32 features from image analysis (radius, texture, etc.)  
- No missing values  
- Target: **Malignant / Benign**

**Cleaning:**
- Removed null column (`Unnamed: 32`)
- Standardized labels (M/B → Malignant/Benign)

---

### 3. METABRIC (Survival Data)
- Clinical + genomic data  
- Includes survival outcomes  

**Cleaning:**
- Removed incomplete records  
- Validated distributions and consistency  

---

## 🗄️ Data Integration
All datasets were cleaned and standardized into a unified database:

```
breast_cancer_analysis.db
```

---

## 📈 Exploratory Data Analysis

We used:
- `seaborn`, `matplotlib`, `plotly`
- Pairplots, histograms, and 3D embeddings (PCA, t-SNE)

### Key Findings

- **Strong separability** between benign and malignant tumors  
- Consistent patterns across both categorical and numerical datasets  
- **No clear separability** for survival prediction (METABRIC)  
- Some indication that **tumor stage may be predictable**

---

## 📷 Visualizations

### Figure 1 – Categorical Histograms
![Figure 1](img/BC_categorical_histogram.png)

### Figure 2 – Categorical Pairplots
![Figure 2](img/BC_categorical_pairplots.png)

### Figure 3 – Numerical Pairplots
![Figure 3](img/Pairplot_numerical.png)

### Figure 4 – Survival Analysis
![Figure 4](img/BC_pairplot_survival_status.png)

### Figure 5 – PCA (Categorical)
![Figure 5](img/3D_PCA_categorical.png)

### Figure 6 – t-SNE (Numerical)
![Figure 6](img/3D_TSNE_numerical.png)

---

## ✅ Conclusions

- Tumor classification is **highly feasible** using statistical features  
- Survival prediction is **not supported** by the current data  
- Tumor stage shows **potential predictive structure**

---

## ⚠️ Challenges
- Selecting the most relevant features  
- Keeping reports concise and readable  
- Visualization and tooling in UNIX environments  

---

## 🚀 Future Work
- Build predictive models for tumor classification  
- Explore advanced models for tumor stage prediction  