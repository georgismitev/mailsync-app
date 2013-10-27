# coding=utf8
import string
import random

from sqlalchemy import Table, Column, Integer, ForeignKey, String, Text, Date, create_engine, desc, delete
from sqlalchemy.orm import relationship, sessionmaker, scoped_session, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Index, UniqueConstraint

from random import randint
from datetime import datetime

def get_emails(number_of_emails):
	emails = []
	[emails.append(get_email()) for number in range(number_of_emails)]

	return emails

def get_email():
	return "".join(random.choice(string.ascii_lowercase + string.digits) for x in range(10)) + "@randomdomain.li"

postgres_engine = create_engine("postgresql://postgres:1234@localhost/testdb5", echo=True)
mysql_engine = create_engine("mysql://root:1234@localhost/testdb")

# engines = {"mysql": mysql_engine, "postgres": postgres_engine }
engines = { "postgres": postgres_engine }
# engines = {"mysql": mysql_engine}
	
for key, engine in engines.iteritems():
	base = declarative_base(bind=engine)
	
	session = scoped_session(sessionmaker(bind=engine))

	class Details(base):
		# __tablename__ = "users"
		__tablename__ = "comments_multiple_choice_website"

		_id = Column(Integer, primary_key=True, autoincrement=True)

		email = Column(String(250), primary_key=True)
		username = Column(String(250))
		age = Column(Integer)
		insert_date = Column(Date)
		website = Column(String(250))
		image_field = Column(String(250))
		comment = Column(String(550))

	base.metadata.create_all()

	# random generation
	emails = get_emails(300)

	comments = [
		# french
		"Supprime le besoin de produire, transférer, exporter et importer des décharges de bases de données, les fichiers CSV et Excel.",
		"Auto-hébergé demande, par conséquent, vous avez le contrôle sur les données et le produit dans votre environnement.",
		"Soyez le premier à entendre parler de mises à jour et des pics-premières de mailsync.",
		# german
		"Entfällt die Notwendigkeit zur Erzeugung, Übertragung, Export und Import Datenbank-Dumps, CSV-und Excel-Dateien.",
		"Self-gehostete Anwendung, deshalb haben Sie die Kontrolle über die Daten und das Produkt in Ihrer Umgebung.",
		"Seien Sie der Erste, der über Updates und Sneak Peaks mailsync hören.",
		# japanese
		"生成、転送する、エクスポート、データベース·ダンプは、CSVファイルやExcelファイルをインポートする必要がなくなります。",
		"セルフホストアプリケーションは、そのためには、データを制御し、ご使用の環境の製品を持っています。",
		"のmailsyncから更新してスニークピークを聞いて最初にしてください。",
	]

	sites = [
		"http://mailsync.li",
		"http://mailsync.li/guide/",
		"http://mailsync.li/help/",
	]

	images = [
		"http://mailsync.li/images/logo.png",
		"http://mailsync.li/images/screens/mailchimp-campaign-monitor-list-database-match.png",
		"http://mailsync.li/images/screens/email-marketing-provider-api.png",
		"http://mailsync.li/images/screens/mysql-postgresql-database.png",
		"http://mailsync.li/images/screens/dashboard-mailchimp-campaign-monitor-lists-synced.png",
		"http://mailsync.li/images/description/mailchimp-and-campaign-monitor-emails-sync.png"
	]

	for index in range(len(emails)):

		mail = emails[index]
		age = randint(10,100)

		session.add(Details(
			username=mail[:10], 
			email=mail,
			age=age, 
			insert_date=datetime.now().strftime("%Y-%m-%d"),
			website=sites[index % 3],
			image_field=images[index % 6],
			comment=comments[index % 9]))
		session.commit()

	session.close()