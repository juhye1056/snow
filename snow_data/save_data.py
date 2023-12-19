from datetime import datetime, timedelta
import requests
from env import settings
from sqlalchemy import Column, create_engine, Integer, String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker

host = settings.DATABASE_CONFIG['host']
database = settings.DATABASE_CONFIG['database']
user = settings.DATABASE_CONFIG['user']
password = settings.DATABASE_CONFIG['password']
port = settings.DATABASE_CONFIG['port']
serviceKey = settings.DATABASE_CONFIG['serviceKey']

engine = create_engine("mysql+pymysql://{}:{}@{}/{}".format(user, password, host, database), echo=True)
Session = sessionmaker(bind=engine)
session = Session()

date_data = datetime.today() - timedelta(1)
date_str = date_data.strftime("%Y%m%d")

"""
전체 구문에 대해

- argument와 return에 Type을 선언해보세요.
- self.aaa = 'aaa'와 같이 self내의 값은 __init__에서 먼저 선언해주세요
- private와 public을 이용해서 변수와 메소드를 수정해보세요
"""


class Base(DeclarativeBase):
    pass


class SnowData(Base):
    __tablename__ = "data_entry"

    # pageNo: Mapped[int] = mapped_column(primary_key=True)
    # stnIds: Mapped[str] = mapped_column(nullable=False)
    # date: Mapped[datetime]
    # ddMefs: Mapped[float]
    # ddMes: Mapped[float]

    pageNo = Column(Integer, primary_key=True)
    stnIds = Column(String(255))
    date = Column(DateTime)
    ddMefs = Column(Float)
    ddMes = Column(Float)
    stnNm = Column(String(255))


Base.metadata.create_all(engine)


class SaveData(object):
    def __init__(self):
        """
        __init__ 메소드 내에서는 주로 객체내 변수를 선언할때 사용합니다. 또한 초기선언이 필요할때 사용합니다(db초기화 등) db, cursor 등 필요한 변수를 넣어보세요
        """
        self.url = "http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList"
        self.params = {
            "serviceKey": serviceKey,
            "pageNo": "1",
            "numOfRows": "1",
            "dataType": "JSON",
            "dataCd": "ASOS",
            "dateCd": "DAY",
            "startDt": date_str,
            "endDt": date_str,
            "stnIds": "108",
        }

        response = requests.get(self.url, params=self.params)
        self.data = response.json()

        for item in self.data['response']['body']['items']['item']:
            ddMes_str = item.get('ddMes')
            ddMes = float(ddMes_str) if ddMes_str else 0.0

            ddMefs_str = item.get('ddMefs')
            ddMefs = float(ddMefs_str) if ddMefs_str else 0.0

            stnNm = item.get('stnNm')

            new_entry = SnowData(
                stnIds=item.get('stnId'),
                date=date_str,
                ddMes=ddMes,
                ddMefs=ddMefs,
                stnNm=stnNm
            )
            session.add(new_entry)
        session.commit()
        session.close()

    # def res_data(self):
    #     """
    #     해당 메소드를 쓰려면 외부에서 res_data(url, params)를 호출해야 합니다. 외부에서가 아니라 내부용으로만 쓰는게 더 적합하지 않을까요?
    #     argument에 url, params를 넣은 이유가 있나요?
    #         -> url, params를 받아와서 사용하는 것인 줄 알고 인자로 url, params를 넣었습니다.
    #     """
    #     # self.data가 아니라 return data 형태로 바꿔보세요. 그리고 이렇게 하는게 더 좋은 이유에 대해서도 생각해보세요

    # def db_sett(self):
    #     """
    #     db 초기 세팅을 하는 메소드로 생각됩니다. 이 메소드는 __init__에서만 실행되도록 만들어보세요.
    #     또한 sql 구문을 보면 테이블을 만드는 구문이라 생각됩니다. 하지만, 이미 테이블이 만들어진 상태라면 해당 구문을 건너뛰어도 되지 않을까요? 이에 대한 코드를 작성해보세요.
    #     """
    #     use_db = "USE snow"
    #     self.cursor.execute(use_db)

    #     table_name = 'snowdata'
    #     self.cursor.execute(f"SHOW TABLES LIKE '{table_name}';")
    #     table_exists = self.cursor.fetchone()

    #     if not table_exists:
    #         self.cursor.execute(f''' CREATE TABLE {table_name} (
    #             ddMes float,
    #             ddMefs float
    #         )
    #     ''')
    #     self.db.commit()

    def table_ins_data(self):
        """
        위 res_data와 마찬가지로 data, db, cursor를 인자로 받을 필요가 없어보입니다.

        """
        ddMes = self.data["response"]["body"]["items"]["item"][0]["ddMes"]
        ddMefs = self.data["response"]["body"]["items"]["item"][0]["ddMefs"]
        if ddMefs == '':
            ddMefs = 0

        if ddMes == '':
            ddMes = 0

        """
        디버그모드로 ddMes와 ddMefs 값을 확인해보세요
        ddMes ='2.2'
        ddMefs = ''
        """

        # ins_query = f"INSERT INTO data_entry (ddMes, ddMefs) VALUES ({ddMes}, {ddMefs})"
        # self.cursor.execute(f""" INSERT INTO snowdata (ddMes, ddMefs) VALUES ({ddMes}, {ddMefs}); """)

        """
        INSERT INTO snowdata (ddMes, ddMefs) VALUES (2.2, )
        cursor.execute(sql) 메소드는 sql 명령어를 인자로 받아서 실행하는 역할을 합니다. 여기서 예시는 대체로 %d, %s 형태로 주는데, 이는 파이썬의 과거 str 선언 방식을 의미합니다.
        최근에는 f-string 방식을 자주사용하는데, 이 형태의 코드로 변형해보세요.
        """
        # self.cursor.execute(ins_query)
        # self.cursor.execute(ins_query, (ddMes[0], ddMefs[0]))

        # self.db.commit()
        # self.db.close()


# 현재 모듈의 이름이 "__main__" 이라면, if문을 실행해라.
if __name__ == "__main__":
    save_data_obj = SaveData()
    save_data_obj.table_ins_data()
