from kafka import KafkaConsumer
import json

#  config for kfka 
kafka_consumer = KafkaConsumer('music_recommendations', boot_server='localhost:9092', reset_offset='latest', grp_id=None, val_deserial=lambda x: json.loads(x.decode('utf-8')))

# Opening  file in writing mode starting  for clearing previous content
with open('recom.txt', 'w') as file:
    file.write('')  #clearing the file at starting

# persestently  listenting  for msgs
for kafka_message in kafka_consumer:
    # Opening file in appending mode to add msgs with not making changes in previous matter
    with open('recom.txt', 'a') as suggestion_file:
        suggestion_file.write(kafka_message.value + '\n')
        print(kafka_message.value)