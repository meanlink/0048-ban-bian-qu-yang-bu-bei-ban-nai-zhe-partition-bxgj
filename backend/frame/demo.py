def seed(cx):
    cx.execute("""
      INSERT INTO board_lots VALUES ('FLEX-17','栖羽 3 mm 纤维背板',3,2.90,.60),
       ('FLEX-20','律窗 5 mm 纤维背板',5,3.30,.50) ON CONFLICT DO NOTHING;
      INSERT INTO flex_fixtures VALUES ('JIG-4','150 mm 夹具',150,3,'2026-12-15',.20),
       ('JIG-OLD','到期 150 mm 夹具',150,3,'2026-10-15',.10),
       ('JIG-5','210 mm 中跨夹具',210,5,'2027-01-15',.10) ON CONFLICT DO NOTHING;
      INSERT INTO backing_samples VALUES ('S-11','FLEX-17','bound','整板 11'),('S-12','FLEX-17','bound','整板 12'),
       ('S-13','FLEX-17','bound','整板 13'),('S-21','FLEX-17','heart','整板 11'),
       ('S-22','FLEX-17','heart','整板 12'),('S-23','FLEX-17','heart','整板 13'),
       ('S-30','FLEX-20','bound','整板 20') ON CONFLICT DO NOTHING;
    """)
    # Demo cards are inserted only once, so excluding one persists through reseeding.
    for sample,value in (("S-11",2.2),("S-12",2.4),("S-13",4.6),("S-21",2.0),("S-22",2.1),("S-23",2.2)):
        cx.execute("""
          INSERT INTO flex_cards(sample,fixture,observed_on,deflection,normalized)
          SELECT %s,'JIG-4','2026-11-19',%s,%s::numeric-.20 WHERE NOT EXISTS
           (SELECT 1 FROM flex_cards WHERE sample=%s)
        """,(sample,value,value,sample))
