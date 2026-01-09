# 导入mysql数据库
import pymysql

class MysqlUtils():
    #初始化
    def __init__(self,host,user,password,db,charset):

        self.host=host
        self.user=user
        self.password=password
        self.db=db
        self.charset=charset
        self.conn = pymysql.connect(host=host, user=user, password=password, db=db, charset=charset)
        self.cur = self.conn.cursor()

    def _ensure(self):
        try:
            self.conn.ping(reconnect=True)
        except Exception:
            self.conn = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db, charset=self.charset)
            self.cur = self.conn.cursor()

    # #增加书籍
    def add_book(self,number,name,author,publicationdate,location ,remark):
        self._ensure()
        # 使用参数化查询防止SQL注入
        sqlstr = "INSERT INTO BOOK (number,name,author,publicationdate,location,remark) VALUES (%s,%s,%s,%s,%s,%s)"
        self.cur.execute(sqlstr, (number, name, author, publicationdate, location, remark))
        # 涉及写操作要注意提交
        self.conn.commit()

    #删除书籍  根据书籍id删除
    def delete_book(self, bookid):
        self._ensure()
        # 使用参数化查询防止SQL注入
        sqlstr = "DELETE FROM BOOK WHERE number = %s"
        self.cur.execute(sqlstr, (bookid,))
        # 涉及写操作要注意提交
        self.conn.commit()

    # #修改书籍    #先删除 后添加  来实现修改功能
    # def change_book(self,number,name,author,publicationdate,location ,remark):

    # 查找所有书籍
    def query_all_book(self):
        self._ensure()
        self.cur.execute('SELECT number ,name,author,publicationdate,location ,remark FROM BOOK order by number')
        result = self.cur.fetchall()
        return result

    #查找指定书籍(参数：书名) 根据书籍名称查询书籍
    def query_one_book(self,name):
        self._ensure()
        # 使用参数化查询防止SQL注入
        sqlstr = "SELECT number,name,author,publicationdate,location,remark FROM BOOK WHERE name = %s"
        self.cur.execute(sqlstr, (name,))
        result = self.cur.fetchall()
        return result

    # 查找指定书籍(参数：书籍id) 根据书籍id查询书籍
    def query_one_book_byid(self, id):
        self._ensure()
        # 使用参数化查询防止SQL注入
        sqlstr = "SELECT number,name,author,publicationdate,location,remark FROM BOOK WHERE number = %s"
        self.cur.execute(sqlstr, (id,))
        result = self.cur.fetchall()
        return result

    # 借阅记录查询（关联读者信息）
    def query_borrowrecord(self):
        self._ensure()
        # 关联student表，获取读者详细信息
        sqlstr = """SELECT b.number, b.name, b.location, b.borrowname, b.borrowtime, 
                   s.class, s.learnnumber, s.phonenumber 
                   FROM BOOK b 
                   LEFT JOIN student s ON b.borrowname = s.name 
                   WHERE b.isborrow = 1 
                   ORDER BY b.borrowtime DESC"""
        self.cur.execute(sqlstr)
        result = self.cur.fetchall()
        return result

    # 查找读者信息
    def query_readerinfor(self):
        self._ensure()
        # 关联user表，显示用户名
        sqlstr = "SELECT s.name,s.class,s.learnnumber,s.phonenumber,s.borrownumber,s.username FROM student s ORDER BY s.id"
        self.cur.execute(sqlstr)
        result = self.cur.fetchall()
        return result
    
    # 根据用户名查询读者信息
    def query_reader_by_username(self, username):
        self._ensure()
        sqlstr = "SELECT id,name,class,learnnumber,phonenumber,borrownumber,username FROM student WHERE username=%s"
        self.cur.execute(sqlstr, (username,))
        result = self.cur.fetchone()
        return result
    
    # 更新读者借书数量
    def update_reader_borrow_count(self, username, increment=1):
        self._ensure()
        sqlstr = "UPDATE student SET borrownumber = borrownumber + %s WHERE username = %s"
        self.cur.execute(sqlstr, (increment, username))
        self.conn.commit()
    
    # 更新读者信息
    def update_reader_info(self, username, reader_name=None, reader_class=None, reader_learn_num=None, reader_phone=None):
        self._ensure()
        updates = []
        params = []
        if reader_name:
            updates.append("name = %s")
            params.append(reader_name)
        if reader_class is not None:
            updates.append("class = %s")
            params.append(reader_class)
        if reader_learn_num is not None:
            updates.append("learnnumber = %s")
            params.append(reader_learn_num)
        if reader_phone is not None:
            updates.append("phonenumber = %s")
            params.append(reader_phone)
        
        if updates:
            params.append(username)
            sqlstr = "UPDATE student SET " + ", ".join(updates) + " WHERE username = %s"
            self.cur.execute(sqlstr, params)
            self.conn.commit()
            return True
        return False

    #注册用户(参数：账号，密码，角色，读者信息)
    def register_Admin(self, username, password, role=None, reader_name=None, reader_class=None, reader_learn_num=None, reader_phone=None):
        self._ensure()
        try:
            # 先插入用户表
            # 尝试检查user表是否有role字段
            user_inserted = False
            if role:
                try:
                    # 尝试插入role字段
                    sqlstr = "INSERT INTO user (username,psw,role) VALUES (%s,%s,%s)"
                    self.cur.execute(sqlstr, (username, password, role))
                    user_inserted = True
                except Exception as role_error:
                    # 如果role字段不存在，回退到不插入role
                    if "Unknown column 'role'" in str(role_error) or "1054" in str(role_error):
                        print("警告: user表没有role字段，将不保存角色信息")
                        sqlstr = "INSERT INTO user (username,psw) VALUES (%s,%s)"
                        self.cur.execute(sqlstr, (username, password))
                        user_inserted = True
                    else:
                        raise role_error
            
            if not user_inserted:
                # 如果没有role，直接插入用户名和密码
                sqlstr = "INSERT INTO user (username,psw) VALUES (%s,%s)"
                self.cur.execute(sqlstr, (username, password))
            
            # 如果是读者，同时创建读者信息
            if role == 'reader' and reader_name:
                try:
                    # 尝试插入带psw的student记录 (为了兼容某些旧表结构可能包含psw字段且无默认值的情况)
                    try:
                        sqlstr = "INSERT INTO student (name,class,learnnumber,phonenumber,borrownumber,username,psw) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                        self.cur.execute(sqlstr, (reader_name, reader_class or '', reader_learn_num or '', reader_phone or '', 0, username, password))
                    except Exception as psw_error:
                         # 如果student表没有psw字段，回退到不插入psw
                        if "Unknown column 'psw'" in str(psw_error) or "1054" in str(psw_error):
                            sqlstr = "INSERT INTO student (name,class,learnnumber,phonenumber,borrownumber,username) VALUES (%s,%s,%s,%s,%s,%s)"
                            self.cur.execute(sqlstr, (reader_name, reader_class or '', reader_learn_num or '', reader_phone or '', 0, username))
                        else:
                            raise psw_error

                except Exception as student_error:
                    # 如果student表没有username字段，尝试不插入username (更旧的表结构)
                    if "Unknown column 'username'" in str(student_error) or "1054" in str(student_error):
                        print("警告: student表没有username字段，将不保存关联")
                        # 这里如果也没有psw，需要再次降级处理，太复杂了，假设没有username的表也不会强制要psw（或者psw在更早的版本中）
                        # 简化处理：尝试最基础的插入
                        try:
                            sqlstr = "INSERT INTO student (name,class,learnnumber,phonenumber,borrownumber,psw) VALUES (%s,%s,%s,%s,%s,%s)"
                            self.cur.execute(sqlstr, (reader_name, reader_class or '', reader_learn_num or '', reader_phone or '', 0, password))
                        except Exception as psw_error2:
                             if "Unknown column 'psw'" in str(psw_error2) or "1054" in str(psw_error2):
                                sqlstr = "INSERT INTO student (name,class,learnnumber,phonenumber,borrownumber) VALUES (%s,%s,%s,%s,%s)"
                                self.cur.execute(sqlstr, (reader_name, reader_class or '', reader_learn_num or '', reader_phone or '', 0))
                             else:
                                 raise psw_error2
                    else:
                        raise student_error
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise e

    #管理员登录(通过账号查询密码)
    def query_Password(self,username):
        self._ensure()
        sqlstr = "SELECT psw FROM user WHERE username=%s"
        self.cur.execute(sqlstr, (username,))
        result = self.cur.fetchall()
        for row in result:
            password=str(row[0])
            return password
        return None

    def borrow_book(self, bookid, borrowname, borrowtime, username=None):
        self._ensure()
        try:
            # 更新图书借阅状态
            sql = "UPDATE BOOK SET isborrow=%s, borrowname=%s, borrowtime=%s WHERE number=%s"
            self.cur.execute(sql, (1, borrowname, borrowtime, bookid))
            
            # 如果提供了username，更新读者借书数量
            if username:
                self.update_reader_borrow_count(username, 1)
            
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def return_book(self, bookid, username=None):
        self._ensure()
        try:
            # 先获取借阅人信息
            borrowname = None
            if username:
                sql_check = "SELECT borrowname FROM BOOK WHERE number=%s AND borrowname IS NOT NULL"
                self.cur.execute(sql_check, (bookid,))
                result = self.cur.fetchone()
                if result:
                    borrowname = result[0]
            
            # 更新图书借阅状态
            sql = "UPDATE BOOK SET isborrow=%s, borrowname=%s, borrowtime=%s WHERE number=%s"
            self.cur.execute(sql, (0, None, None, bookid))
            
            # 如果提供了username，更新读者借书数量
            if username:
                self.update_reader_borrow_count(username, -1)
            
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def query_all_book_with_borrow(self):
        self._ensure()
        sql = "SELECT number,name,author,publicationdate,location,remark,isborrow FROM BOOK ORDER BY number"
        self.cur.execute(sql)
        return self.cur.fetchall()
