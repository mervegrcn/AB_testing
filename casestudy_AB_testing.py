#####################################################
# AB Testi ile BiddingYöntemlerinin Dönüşümünün Karşılaştırılması
#####################################################
import pandas as pd

#####################################################
# İş Problemi
#####################################################

# Facebook kısa süre önce mevcut "maximumbidding" adı verilen teklif verme türüne alternatif
# olarak yeni bir teklif türü olan "average bidding"’i tanıttı. Müşterilerimizden biri olan bombabomba.com,
# bu yeni özelliği test etmeye karar verdi veaveragebidding'in maximumbidding'den daha fazla dönüşüm
# getirip getirmediğini anlamak için bir A/B testi yapmak istiyor.A/B testi 1 aydır devam ediyor ve
# bombabomba.com şimdi sizden bu A/B testinin sonuçlarını analiz etmenizi bekliyor.Bombabomba.com için
# nihai başarı ölçütü Purchase'dır. Bu nedenle, istatistiksel testler için Purchasemetriğine odaklanılmalıdır.



#####################################################
# Veri Seti Hikayesi
#####################################################

# Bir firmanın web site bilgilerini içeren bu veri setinde kullanıcıların gördükleri ve tıkladıkları
# reklam sayıları gibi bilgilerin yanı sıra buradan gelen kazanç bilgileri yer almaktadır.Kontrol ve Test
# grubu olmak üzere iki ayrı veri seti vardır. Bu veri setleriab_testing.xlsxexcel’ininayrı sayfalarında yer
# almaktadır. Kontrol grubuna Maximum Bidding, test grubuna AverageBiddinguygulanmıştır.

# impression: Reklam görüntüleme sayısı
# Click: Görüntülenen reklama tıklama sayısı
# Purchase: Tıklanan reklamlar sonrası satın alınan ürün sayısı
# Earning: Satın alınan ürünler sonrası elde edilen kazanç



#####################################################
# Proje Görevleri
#####################################################

######################################################
# AB Testing (Bağımsız İki Örneklem T Testi)
######################################################

# 1. Hipotezleri Kur
# 2. Varsayım Kontrolü
#   - 1. Normallik Varsayımı (shapiro)
#   - 2. Varyans Homojenliği (levene)
# 3. Hipotezin Uygulanması
#   - 1. Varsayımlar sağlanıyorsa bağımsız iki örneklem t testi
#   - 2. Varsayımlar sağlanmıyorsa mannwhitneyu testi
# 4. p-value değerine göre sonuçları yorumla
# Not:
# - Normallik sağlanmıyorsa direkt 2 numara. Varyans homojenliği sağlanmıyorsa 1 numaraya arguman girilir.
# - Normallik incelemesi öncesi aykırı değer incelemesi ve düzeltmesi yapmak faydalı olabilir.




#####################################################
# Görev 1:  Veriyi Hazırlama ve Analiz Etme
#####################################################

# Adım 1:  ab_testing_data.xlsx adlı kontrol ve test grubu verilerinden oluşan veri setini okutunuz. Kontrol ve test grubu verilerini ayrı değişkenlere atayınız.

import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
pip install statsmodels
import statsmodels.stats.api as sms
from scipy.stats import ttest_1samp, shapiro, levene, ttest_ind, mannwhitneyu, \
    pearsonr, spearmanr, kendalltau, f_oneway, kruskal
from statsmodels.stats.proportion import proportions_ztest

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 10)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df = pd.read_excel("/Users/mervegurcan/PycharmProjects/pythonProject/DATASETS/ab_testing.xlsx", sheet_name = "Control Group")
df2 = pd.read_excel("/Users/mervegurcan/PycharmProjects/pythonProject/DATASETS/ab_testing.xlsx", sheet_name = "Test Group")

# Adım 2: Kontrol ve test grubu verilerini analiz ediniz.

df.describe().T
df.shape
df.info()

df2.describe(). T
df2.shape
df2.info()

# Adım 3: Analiz işleminden sonra concat metodunu kullanarak kontrol ve test grubu verilerini birleştiriniz.

# Kontrol Group - Max bidding
# Test Group - Average Bidding

# Control_and_test_concat = pd.concat([df, df2], axis = 1) KOLONLARI YANYANA EKLER

#kolonları alt alta ekler
all_df = pd.concat([df, df2], axis = 0).reset_index()
# all_df.drop("index",axis=1,inplace=True)

all_df.shape

all_df["group"] = ["control" if index < 40 else "test" for index in all_df.index]

all_df.head()
all_df.tail()
all_df.columns


#####################################################
# Görev 2:  A/B Testinin Hipotezinin Tanımlanması
#####################################################

# Adım 1: Hipotezi tanımlayınız.

# H0: Average bidding ve Maximum bidding dönüşüm oranları arasında fark yoktur
# H1: Average bidding ve Maximum bidding dönüşüm oranları arasında fark vardır

# Adım 2: Kontrol ve test grubu için purchase(kazanç) ortalamalarını analiz ediniz

all_df.groupby("group").agg({"Purchase": "mean"})

#OUTPUT
#         Purchase
#group
#control 550.89406
#test    582.10610

#ALTERNATIF
#1
all_df.loc[(all_df["group"] == "control"), ["Purchase"]].mean()
all_df.loc[(all_df["group"] == "test"), ["Purchase"]].mean()
#2
all_df[all_df["group"] == "control"]["Purchase"].mean()
all_df[all_df["group"] == "test"]["Purchase"].mean()


#### YORUM: ####
# Matematiksel olarak aralarında fark var.
# Test (average billing) yönteminin satın alması, Kontrol (Maximum bidding) yönteminin satın almasından MATEMATİKSEL olarak daha iyi gibi gözüküyor.
# Testlerle İSTATİKSEL duruma bakalım

#####################################################
# GÖREV 3: Hipotez Testinin Gerçekleştirilmesi
#####################################################

######################################################
# AB Testing (Bağımsız İki Örneklem T Testi)col
######################################################

# Adım 1: Hipotez testi yapılmadan önce varsayım kontrollerini yapınız.Bunlar Normallik Varsayımı ve Varyans Homojenliğidir.

# Kontrol ve test grubunun normallik varsayımına uyup uymadığını Purchase değişkeni üzerinden ayrı ayrı test ediniz

#NORMALLİK VARSAYIMI

# H0: Normal dağılım varsayımı sağlanmaktadır.
# H1: Normal dağılım varsayımı sağlanmamaktadır.

# shapiro testi: bir değişkenin dağılımının normal olup olmadığını test eder.

test_stat, pvalue = shapiro(all_df.loc[all_df["group"] == "control", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

#OUTPUT: Test Stat = 0.9773, p-value = 0.5891

test_stat, pvalue = shapiro(all_df.loc[all_df["group"] == "test", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

#OUTPUT: Test Stat = 0.9589, p-value = 0.1541

# p value'lar 0.05'den büyük olduğu için H0 reddedilemez yani normal dağılım vardır.

#HOMOJENLIK VARSAYIMI

# H0: Varyanslar Homojendir
# H1: Varyanslar Homojen Değildir

# levene: iki farklı gruba göre varyans homejenliğinin sağlanıp sağlanmadığını ifade eder

test_stats, pvalue = levene(all_df.loc[all_df["group"] == "control", "Purchase"],
                            all_df.loc[all_df["group"] == "test", "Purchase"])
print("Test Stat = %.4f, p-value = %.4f" % (test_stat, pvalue))

#OUTPUT: Test Stat = 0.9589, p-value = 0.1083

# p value 0.05 den büyük olduğu için normal dağılım vardır.

# Adım 2: Normallik Varsayımı ve Varyans Homojenliği sonuçlarına göre uygun testi seçiniz

# 1. Varsayımlar sağlanıyorsa bağımsız iki örneklem t testi (parametrik test)
# 2. Varsayımlar sağlanmıyorsa mannwhitneyu testi (non-parametrik test)

# iki varsayım da sağlandığı için ttest uygulayabiliriz

test_stat, pvalue = ttest_ind(all_df.loc[all_df["group"] == "control", "Purchase"],
                              all_df.loc[all_df["group"] == "test", "Purchase"],
                              equal_var=True)
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

#OUTPUT: Test Stat = -0.9416, p-value = 0.3493

# EK BİLGİ #
# normallik varsayımı sağlanıyor, homejenlik varsayımı sağlanmıyor olsaydı ttestini saşağıdaki gibi kullanırız:
test_stat, pvalue = ttest_ind(all_df.loc[all_df["group"] == "control", "Purchase"],
                              all_df.loc[all_df["group"] == "test", "Purchase"],
                              equal_var=False)
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

# Adım 3: Test sonucunda elde edilen p_value değerini göz önünde bulundurarak kontrol ve test grubu satın alma
# ortalamaları arasında istatistiki olarak anlamlı bir fark olup olmadığını yorumlayınız.

# H0: Average bidding ve Maximum bidding dönüşüm oranları arasında fark yoktur
# H1: Average bidding ve Maximum bidding dönüşüm oranları arasında fark vardır

# p value > 0.05 çıktı. Yani H0 reddedilemedi. Bu da yeni teklif ürünü olan average bidding ile mevcut olan maximum bidding
# teklif ürünü arasında satın alma yönünden İSTATİKSEL olarak fark olmadığını göstermektedir. MATEMATİKSEL fark rastlantı sonucu oluşmuştur.

##############################################################
# GÖREV 4 : Sonuçların Analizi
##############################################################

# Adım 1: Hangi testi kullandınız, sebeplerini belirtiniz.

# shapiro testi: normal dağılım olup olmadığını kontrol etmek için
# levene: iki farklı gruba göre varyans homejenliğinin sağlanıp sağlanmadığını kontrol için
# ttest: normal dağılım ve varyans homojenliği varsayımları, birlikte sağlandığı için kullandık

# mannwhitneyu: Varsayımlar sağlanmasaydı mannwhitneyu testi (non-parametrik test)'ini kullanacaktık.

# Adım 2: Elde ettiğiniz test sonuçlarına göre müşteriye tavsiyede bulununuz.

# maximum bidding (maksimum teklif) ile average bidding (ortalama teklif) arasında istatiksel anlamda satın alınan ürün sayısında
# bir fark olmadığını gördüğümüz için yeni teklif türü olan average bididng için ekstra iş güc ayırmaya gerek olmadığı görülüyor.