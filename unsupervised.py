# -*- coding: utf-8 -*-
"""Unsupervised.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GzymmUc99zxUyVldrHX_YEc3QubkAlxh

### Importing "stock_market_data.csv"
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Load the dataset
data = pd.read_csv('stock_market_data.csv')

# Preview the data
print("Original Data:")
data.head()

data.info()

data.describe()

data['Profit_Category'] = pd.cut(data['PercentageChange'],
                                   bins=[-float('inf'), -10, 0, 10, float('inf')],
                                   labels=['High Loss', 'Loss', 'Moderate Profit', 'High Profit'],
                                   include_lowest=True,
                                   right=False

                                  )
data

# Keep only numeric columns
numeric_data = data.select_dtypes(include=[np.number])
print("Numeric Data:")
numeric_data

# Normalize the data using StandardScaler
scaler = StandardScaler()
scaled_data = scaler.fit_transform(numeric_data)
pd.DataFrame(scaled_data, columns=numeric_data.columns).head()

# PCA with 2 components
pca_2d = PCA(n_components=2)
data_pca_2d = pca_2d.fit_transform(scaled_data)
explained_var_2d = pca_2d.explained_variance_ratio_.sum() * 100
print(f"2D PCA retains {explained_var_2d:.2f}% of the variance")

# Plot 2D projection
plt.figure(figsize=(8, 6))
plt.scatter(data_pca_2d[:, 0], data_pca_2d[:, 1], alpha=0.5,c='blue')
plt.title('2D PCA Projection')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.grid(True)
plt.show()

# PCA with 3 components
pca_3d = PCA(n_components=3)
data_pca_3d = pca_3d.fit_transform(scaled_data)
explained_var_3d = pca_3d.explained_variance_ratio_.sum() * 100
print(f"3D PCA retains {explained_var_3d:.2f}% of the variance")

# Plot 3D projection
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(data_pca_3d[:, 0], data_pca_3d[:, 1], data_pca_3d[:, 2], alpha=0.5,c='blue')
ax.set_title('3D PCA Projection')
ax.set_xlabel('PC 1')
ax.set_ylabel('PC 2')
ax.set_zlabel('PC 3')
plt.show()

# Calculate the number of components to retain at least 95% variance
pca_full = PCA().fit(scaled_data)

# Explained variance ratio
explained_variance_ratio = pca_full.explained_variance_ratio_

# Cumulative explained variance
cumulative_variance = np.cumsum(explained_variance_ratio)

# Plot explained variance
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.bar(range(1, len(explained_variance_ratio) + 1), explained_variance_ratio)
plt.xlabel('Principal Component')
plt.ylabel('Explained Variance Ratio')
plt.title('Explained Variance Ratio per Principal Component')

# Plot cumulative explained variance
plt.subplot(1, 2, 2)
plt.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, marker='o')
plt.xlabel('Number of Components')
plt.ylabel('Cumulative Explained Variance')
plt.title('Cumulative Explained Variance')
plt.axhline(y=0.95, color='r', linestyle='--', label='95% Threshold')  # Add 95% threshold line
plt.legend()

plt.tight_layout()
plt.show()

eigenvalues = pca_full.explained_variance_

# Get the top three eigenvalues
top_three_eigenvalues = eigenvalues[:3]

# Print the top three eigenvalues
print("Top three eigenvalues:", top_three_eigenvalues)

"""### Clustering"""

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score # Import silhouette_score

#Reduced 3D pca data
df_cluster = data_pca_3d

# Finding the optimal K using the silhouette method
silhouette_scores = {}
for k in range(2, 6):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(df_cluster)
    silhouette_scores[k] = silhouette_score(df_cluster, cluster_labels)

silhouette_scores

optimal_k = max(silhouette_scores, key=silhouette_scores.get)
print(f"Optimal number of clusters for KMeans: {optimal_k}")

# Plot the Silhouette Scores for different K values
plt.figure(figsize=(8, 5))
plt.plot(list(silhouette_scores.keys()), list(silhouette_scores.values()), marker='o', linestyle='-')
plt.xlabel("Number of Clusters (K)")
plt.ylabel("Silhouette Score")
plt.title("Silhouette Scores for Different K in K-Means")
plt.xticks(list(silhouette_scores.keys()))
plt.grid(True)
plt.show()

# Applying KMeans with optimal K
kmeans_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df_kmeans_labels = kmeans_final.fit_predict(df_cluster)

# Get the centroids in the PCA-reduced space
centroids_pca_space = kmeans_final.cluster_centers_

# Use pca_3d for inverse_transform
centroids_original_space = pca_3d.inverse_transform(centroids_pca_space)

# Print the centroids in the PCA-reduced space
print("Centroids in PCA-reduced space:")
print(centroids_pca_space)

print("\nCentroids in original feature space:")
print(centroids_original_space)

# Applying KMeans with optimal K
kmeans_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df_kmeans_labels = kmeans_final.fit_predict(df_cluster)

# Get centroids
centroids = kmeans_final.cluster_centers_

# Plot KMeans Clustering in 2D
plt.figure(figsize=(8, 6))
plt.scatter(df_cluster[:, 0], df_cluster[:, 1], c=df_kmeans_labels, cmap='viridis', alpha=0.7)
plt.scatter(centroids[:, 0], centroids[:, 1], marker='x', s=200, c='red', label='Centroids') # Plot centroids
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.title(f"K-Means Clustering (K={optimal_k})")
plt.legend() # Show legend to identify centroids
plt.show()

"""### DBSCAN"""

from sklearn.cluster import DBSCAN

# Initialize and fit DBSCAN
dbscan = DBSCAN(eps=0.5, min_samples=5)
df_dbscan_labels = dbscan.fit_predict(df_cluster)

plt.figure(figsize=(8, 6))
plt.scatter(df_cluster[:, 0], df_cluster[:, 1], c=df_dbscan_labels, cmap='coolwarm', alpha=0.7)
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.title("DBSCAN Clustering")
plt.show()

import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as sch
import numpy as np

# Mapping of numerical labels to stock tickers
ticker_mapping = {
    1: 'AAPL', 2: 'MSFT', 3: 'GOOGL', 4: 'TSLA', 5: 'AMZN',
    6: 'NVDA', 7: 'META', 8: 'NFLX', 9: 'AMD', 10: 'BA'
}

# Generate dummy data for clustering
np.random.seed(42)
data = np.random.rand(len(ticker_mapping), 2)  # Assume 2D feature space
linkage_matrix = sch.linkage(data, method='ward')

# Plot dendrogram with meaningful labels
plt.figure(figsize=(12, 6))
dendro = sch.dendrogram(linkage_matrix, labels=[ticker_mapping.get(i+1, i+1) for i in range(len(ticker_mapping))], leaf_rotation=90)
plt.title("Hierarchical Clustering Dendrogram with Stock Names")
plt.xlabel("Stock Names")
plt.ylabel("Distance")
plt.show()

"""### Preparing data (converting) to perform ARM"""

data = pd.read_csv('stock_market_data.csv')
data

data['Price_Change_Category'] = pd.cut(data['Daily_Change'],
                                       bins=[-float('inf'), -2, 0, 2, float('inf')],
                                       labels=['Big Drop', 'Small Drop', 'Small Rise', 'Big Rise'])

data

data['Trade_Volume'] = pd.qcut(data['Volume'], q=4,
                                 labels=['Very Low', 'Low', 'High', 'Very High'])
data

data['Trend_Strength'] = pd.cut(data['PercentageChange'],
                                bins=[-float('inf'), -5, -2, 0, 2, 5, float('inf')],
                                labels=['Strong Loss', 'Moderate Loss', 'Small Loss', 'Small Gain', 'Moderate Gain', 'Strong Gain'])
data

tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META']
consumer_stocks = ['AMZN', 'NFLX']
industrial_stocks = ['BA', 'AMD']

data['Sector'] = data['Ticker'].apply(lambda x: 'Tech' if x in tech_stocks
                                      else 'Consumer' if x in consumer_stocks
                                      else 'Industrial')
data

# Dropping 'Ticker' and 'Date' columns
df_final = data.drop(columns=['Date','Open', 'High','Low','Close', 'Ticker', 'Volume', 'Daily_Change', 'PercentageChange'])
df_final

df_final.columns = [''] * len(df_final.columns)

df_final.head()

df_final.to_csv('ARM_data.csv', index=False)