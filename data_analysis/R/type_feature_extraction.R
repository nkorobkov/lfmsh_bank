library("dplyr")
# need this to show russian characters
Sys.setlocale("LC_CTYPE", "ru_RU")

# prepare data
money = read.csv('../data/money.csv',sep=',', stringsAsFactors=FALSE, encoding = "UTF-8")
money = as_data_frame(money) %>%
  filter(counted == 'True', receiver_username != 'pioner_bankir') %>%
  mutate(creation_timestamp = as.POSIXct(creation_timestamp, format = "%d.%m.%Y %H:%M")) %>%
  arrange(creation_timestamp) 


counters = read.csv('../data/counters.csv',sep=',', stringsAsFactors=FALSE, encoding = "UTF-8")
counters = as_data_frame(counters) %>%
  filter(counted == 'True', receiver_username != 'pioner_bankir' ) %>%
  mutate(creation_timestamp = as.POSIXct(creation_timestamp, format = "%d.%m.%Y %H:%M")) %>%
  arrange(creation_timestamp)

#


###feature extraction
##money
# basic info by type
type_money_atomic_features = money %>%
  group_by(type_readable_name) %>%
  summarise(num_of_atomics = n(),
            total_value = sum(value),
            max_atomic_value = max(value),
            min_atomic_value = min(value),
            median_atomic_value = median(value),
            mean_atomic_value = mean(value)
            
            ) %>%
  arrange(type_readable_name)

type_money_features = money %>%
  group_by(type_readable_name, creation_timestamp) %>%
  summarise(value = sum(value)) %>%
  group_by(type_readable_name) %>%
  summarise(num_of_transactions = n(),
            mean_transaction = mean(value)
            ) %>%
  arrange(type_readable_name)

type_money_features_table = left_join(type_money_features, type_money_atomic_features, by='type_readable_name') %>%
  arrange(total_value)
  
## by local types

type_local_money_atomic_features = money %>%
  group_by(type_group_local) %>%
  summarise(num_of_atomics = n(),
            total_value = sum(value),
            max_atomic_value = max(value),
            min_atomic_value = min(value),
            median_atomic_value = median(value),
            mean_atomic_value = mean(value)) 

type_local_money_features = money %>%
  group_by(type_group_local, creation_timestamp) %>%
  summarise(value = sum(value)) %>%
  group_by(type_group_local) %>%
  summarise(num_of_transactions = n(),
            mean_transaction = mean(value)) 

type_local_money_features_table = left_join(type_local_money_atomic_features, type_local_money_features, by='type_group_local') %>%
  mutate (type_readable_name = paste0("Все ", type_group_local)) %>%
  select(-type_group_local) %>%
  arrange(total_value)


### By global types


type_general_money_atomic_features = money %>%
  group_by(type_group_general) %>%
  summarise(num_of_atomics = n(),
            total_value = sum(value),
            max_atomic_value = max(value),
            min_atomic_value = min(value),
            median_atomic_value = median(value),
            mean_atomic_value = mean(value)) 

type_general_money_features = money %>%
  group_by(type_group_general, creation_timestamp) %>%
  summarise(value = sum(value)) %>%
  group_by(type_group_general) %>%
  summarise(num_of_transactions = n(),
            mean_transaction = mean(value)) 

type_general_money_features_table = left_join(type_general_money_atomic_features, type_general_money_features, by='type_group_general') %>%
  mutate (type_readable_name = paste0("Все ", type_group_general)) %>%
  select(-type_group_general) %>%
  arrange(total_value)


### Counters
# book cert duplication to see flow
certificate_transactions = counters %>%
  filter(type_readable_name == 'Сертификат на книжки')
add_certificates = filter(certificate_transactions, value>0) %>% mutate(type_readable_name = 'Получено сертификатов')
sub_certificates = filter(certificate_transactions, value<0) %>% mutate(type_readable_name = 'Потрачено сертификатов')

counters = bind_rows(filter(counters,type_readable_name != 'Сертификат на книжки'), add_certificates, sub_certificates)




type_counters_atomic_features = counters %>%
  group_by(type_readable_name) %>%
  summarise(num_of_atomics = n(),
            total_value = sum(value),
            max_atomic_value = max(value),
            min_atomic_value = min(value),
            median_atomic_value = median(value),
            mean_atomic_value = mean(value)) 

type_counters_features = counters %>%
  group_by(type_readable_name, creation_timestamp) %>%
  summarise(value = sum(value)) %>%
  group_by(type_readable_name) %>%
  summarise(num_of_transactions = n(),
            mean_transaction = mean(value)) 

type_counter_features_table = left_join(type_counters_features, type_counters_atomic_features, by='type_readable_name') %>%
  arrange(total_value)

type_features = bind_rows(type_counter_features_table,type_general_money_features_table,type_local_money_features_table,type_money_features_table)


write.csv(type_features, '../data/type_features.csv')

 
