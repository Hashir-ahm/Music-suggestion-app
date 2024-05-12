from pyspark.sql import spark_sess
from pyspark.sql.functions import column, split, reg_replace, udf
from pyspark.sql.types import ArrayType, DoubleType, IntegerType, StringType
from pyspark.ml.recommendation import ALS
from pyspark.ml.feature import StringIndexer
from pyspark.sql.functions import expr
from kafka import KafkaProducer
import json

# Initialize the session 
sparksess = spark_sess.builder \
    .appName("Music Recommendation System") \
    .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/mfcc_db.mfcc_columnlection") \
    .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/mfcc_db.mfcc_columnlection") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .getOrCreate()

# starting the  Kafka Producer
kafka_producer = KafkaProducer(b_serversss='localhost:9092', val_serial=lambda v: json.dumps(v).encode('utf-8'))

# Loading the  data from mongo
mong__dfram = sparksess.read.format("com.mongodb.spark.sql.DefaultSource").load()

# columnlect track IDs
track_ids = mong__dfram.select("track_id").rdd.flatMap(lambda x: x).columnlect()

# Data preprocessing
mong_dfram = mong_dfram.withcolumnumn("genre_all", split(reg_replace(column("genre_all"), r"[\[\]]", ""), ", ").cast(ArrayType(IntegerType())))
mong_dfram = mong_dfram.withcolumnumn("mfcc_features", column("mfcc_features").cast(ArrayType(DoubleType())))
mfcc_features_df = mong__dfram.select(column("mfcc_features"))

# Define UDF to extract 
extract_first_element_udf = udf(lambda x: str(x[0]) if x else None, StringType())

# new DataFrame with features extracted
features_df = mfcc_features_df.withcolumnumn("features", extract_first_element_udf("mfcc_features")).select("features")

# Index features
feature_indexer = StringIndexer(inputcolumn="features", outputcolumn="featureindex")
indexed_features_df = feature_indexer.fit(features_df).transform(features_df)

# Add rating columnumn
indexed_features_df = indexed_features_df.withcolumnumn("rating", column("featureindex").cast(IntegerType()))
indexed_features_df = indexed_features_df.withcolumnumn("random_columnumn", column("features").cast(IntegerType()))

# Train ALS model
als_model = ALS(maximumlter=10, reg_param=0.01, user_columnumn="featureindex", itemscolumn="rating", rating_columnumn="random_columnumn",
                columndStartStrategy="drop")
model_fitted = als_model.fit(indexed_features_df)

# Get top recommendations for all users
feature_recommendations = model_fitted.recommendForAllUsers(5)

# Define target feature index
target_feature_index = 12

# Filter recommendations for target feature index
filtered_recommendations = feature_recommendations.filter(feature_recommendations["featureindex"] == target_feature_index).select("recommendations")

filtered_recommendations_df = filtered_recommendations.toPandas()

# Extraction for recommendations
recommendations_lis = filtered_recommendations_df['recommendations'].iloc[0]

# Extraction for  the  values for  recommendations
first_values_lis = [lis(items)[0] for items in recommendations_lis]

for index in first_values_lis:
    kafka_producer.send('music_recommendations are ', value=track_ids[index])

# Flush Kafka producer
kafka_producer.flush()