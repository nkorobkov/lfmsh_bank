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

# prepare p2p transactions to grouping
p2p_money_to_add = money %>%
  filter(type_readable_name=='Личный перевод') %>%
  mutate(receiver_username = transaction_creator_username, transaction_creator_username = receiver_username, value = -value)
 money = bind_rows(money, p2p_money_to_add)
 


###feature extraction
 ##money
 # basic info
money_features = money %>%
  group_by(receiver_username) %>%
  summarise(username = first(receiver_username),
            first_name = first(receiver_first_name),
            last_name = first(receiver_last_name),
            grade = factor(first(receiver_grade)),
            party = factor(first(receiver_party)),
            final_balance = sum(value)) %>%
  arrange(receiver_username)


# by type name
money_type_features = money %>%
  group_by(receiver_username, type_readable_name) %>%
  summarise(username = first(receiver_username) ,value = sum(value))
money_type_features_table = as.data.frame.matrix(xtabs(value~username+type_readable_name, data= money_type_features))

# by type local group
local_type_features = money %>%
  group_by(receiver_username, type_group_local) %>%
  summarise(username = first(receiver_username) ,value = sum(value))
local_type_features_table = as.data.frame.matrix(xtabs(value~username+type_group_local, data= local_type_features))
# set prefix to columnnames no avoid collisions
colnames(local_type_features_table) <- paste("Частные", colnames(local_type_features_table), sep = " ")

#by type general group
general_type_features = money %>%
  group_by(receiver_username, type_group_general) %>%
  summarise(username = first(receiver_username) ,value = sum(value))
general_type_features_table = as.data.frame.matrix(xtabs(value~username+type_group_general, data= general_type_features))
colnames(general_type_features_table) <- paste("Общие", colnames(general_type_features_table), sep = " ")

#build one table
money_features = bind_cols(money_features, money_type_features_table, local_type_features_table, general_type_features_table)
# total earnings = sum of all positive categories  without technical types
money_features = mutate(money_features, "Заработано за смену" = `Общие Другое` + `Общие Мероприятие` +`Общие Спорт` +`Общие Оплата труда` +`Общие Переводы` + `Общие Учеба`)

### Counters feature extraction

# book cert duplication to see flow
certificate_transactions = counters %>%
  filter(type_readable_name == 'Сертификат на книжки')
add_certificates = filter(certificate_transactions, value>0) %>% mutate(type_readable_name = 'Получено сертификатов')
sub_certificates = filter(certificate_transactions, value<0) %>% mutate(type_readable_name = 'Потрачено сертификатов')

counters = bind_rows(filter(counters,type_readable_name != 'Сертификат на книжки'), add_certificates, sub_certificates)



counter_features = counters %>%
  group_by(receiver_username, type_readable_name) %>%
  summarise(username = first(receiver_username) ,value = sum(value))



counter_features_table = as.data.frame.matrix(xtabs(value~username+type_readable_name, data= counter_features)) %>%
  mutate("Осталось Сертификатов" = `Получено сертификатов` + `Потрачено сертификатов`)

colnames(counter_features_table) <- paste("Счетчик", colnames(counter_features_table), sep = " ")


student_features = bind_cols(money_features, counter_features_table)

write.csv(student_features, '../data/student_features.csv')

