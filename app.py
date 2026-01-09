# MVC模式
# controller层

from flask import Flask, render_template, flash, request, abort, redirect, url_for, session, jsonify
import os
import urllib.request
import urllib.error
import re
# from models import User
# 导入数据库操作工具类
from mysqlUtils import MysqlUtils
# 导入json包
import json
import traceback

# MVC模式model层
from models.readerModel import readerModel
from models.recordModel import recordModel
from models.bookModel import bookModel

# 导入配置和DeepSeek服务
from config import Config
from deepseek_service import get_deepseek_service

# 使用配置初始化数据库连接
util = MysqlUtils(Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, Config.DB_NAME, Config.DB_CHARSET)

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY  # flash加密


@app.route('/')
def hello_world():
    flash("")  # 登陆注册提示信息
    content = "hello world"
    # return render_template("login.html", content=content)
    return render_template("login.html", content=content)


# 注册
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        form = request.form
        username = form.get('username')
        password = form.get('password')
        password2 = form.get('password2')
        role = form.get('role') or 'reader'
        # 前端完成判断内容是否为空
        if not username:
            flash("请输入用户名")
            return render_template("register.html")
        if not password:
            flash("请输入密码")
            return render_template("register.html")
        if not password2:
            flash("请输入确认密码")
            return render_template("register.html")
        if not password == password2:
            flash("两次密码不一致")
            return render_template("register.html")
        else:  # 注册信息无误，写入数据库
            try:
                # 如果是读者，获取读者信息
                reader_name = None
                reader_class = None
                reader_learn_num = None
                reader_phone = None
                
                if role == 'reader':
                    reader_name = (form.get('reader_name') or '').strip()
                    reader_class = (form.get('reader_class') or '').strip()
                    reader_learn_num = (form.get('reader_learn_num') or '').strip()
                    reader_phone = (form.get('reader_phone') or '').strip()
                    
                    if not reader_name:
                        flash("读者注册必须填写姓名")
                        return render_template("register.html")
                
                # 注册用户并创建读者信息
                util.register_Admin(username, password, role, reader_name, reader_class, reader_learn_num, reader_phone)
                flash("注册成功")
                return render_template("register.html")
            except Exception as e:
                print(f"注册错误: {str(e)}")
                print(traceback.format_exc())
                flash(f"注册失败: {str(e)}")
                return render_template("register.html")
    else:
        return render_template("register.html")


# 登录界面路由
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        form = request.form
        username = form.get('username') + ""
        password = form.get('password') + ""
        role = (form.get('role') or "admin") + ""
        if not username:
            flash("请输入用户名")
            return render_template("login.html", password=password)
        if not password:
            flash("请输入密码")
            return render_template("login.html", username=username)
        password2 = util.query_Password(username)  # 根据账号查询的密码
        if (password == password2):
            session['username'] = username
            session['role'] = role
            if role == 'reader':
                return redirect(url_for('reader_querybook'))
            else:
                return render_template("addbook.html")
        else:
            flash("用户名或密码错误")
            return render_template("login.html", username=username, password=password)
    else:  # 请求方式为GET时
        return render_template("login.html")
        # if username == 'lipiao' and password == '123':
        #     flash("登录成功")
        #     # 默认显示为查询页面
        #     return render_template("addbook.html")
        #     # 先设置为跳转至百度
        #     # return redirect("http://www.baidu.com")


# util.add_book(number,name,author,publicationdate,location,remark)
# MVC模式代码重构
# 增加书籍界面 # number ,name,author,publicationdate,location ,remark
@app.route('/addbook', methods=['POST', 'GET'])
def addbook():
    try:
        if request.method == "POST":
            form = request.form
            number = (form.get('number') or '').strip()
            name = (form.get('bookname') or '').strip()
            author = (form.get('author') or '').strip()
            publicationdate = (form.get('pdate') or '').strip()
            location = (form.get('address') or '').strip()
            remark = (form.get('description') or '').strip()
            
            if not number:
                flash("请输入id")
                return render_template("addbook.html", number=number, name=name, author=author, 
                                     publicationdate=publicationdate, location=location, remark=remark)
            if not name:
                flash("请输入书名")
                return render_template("addbook.html", number=number, name=name, author=author,
                                     publicationdate=publicationdate, location=location, remark=remark)
            if not location:
                flash("请输入位置")
                return render_template("addbook.html", number=number, name=name, author=author,
                                     publicationdate=publicationdate, location=location, remark=remark)
            
            # 检查是否已存在相同ID的图书
            existing = util.query_one_book_byid(number)
            if existing:
                flash(f"图书ID {number} 已存在，请使用不同的ID")
                return render_template("addbook.html", number=number, name=name, author=author,
                                     publicationdate=publicationdate, location=location, remark=remark)
            
            m = bookModel()
            m.add_book(number, name, author, publicationdate, location, remark)
            flash("添加图书成功")
            return render_template("addbook.html")
        else:
            return render_template("addbook.html")
    except Exception as e:
        print(f"添加图书错误: {str(e)}")
        print(traceback.format_exc())
        flash(f"添加图书失败: {str(e)}")
        return render_template("addbook.html")


# 删除书籍界面
@app.route('/deletebook', methods=['GET', 'POST'])
def deletebook():
    # u = util.query_all_book()
    # MVC模式重构
    m = bookModel()
    books = m.get_all_book_data()
    return render_template("deletebook.html", books=books)


# 负责删除书籍的路由 带参数：书籍ID
@app.route('/deletebook2/<bookid>', methods=['GET'])
def deletebook2(bookid):
    try:
        # 检查图书是否存在
        existing = util.query_one_book_byid(bookid)
        if not existing:
            flash(f"图书ID {bookid} 不存在")
            m = bookModel()
            books = m.get_all_book_data()
            return render_template("deletebook.html", books=books)
        
        # MVC模式重构
        m = bookModel()
        m.delete_one_book_by_id(bookid)
        books = m.get_all_book_data()
        flash(f"成功删除图书ID: {bookid}")
        return render_template("deletebook.html", books=books)
    except Exception as e:
        print(f"删除图书错误: {str(e)}")
        print(traceback.format_exc())
        flash(f"删除图书失败: {str(e)}")
        m = bookModel()
        books = m.get_all_book_data()
        return render_template("deletebook.html", books=books)


# 修改书籍界面
@app.route('/changebook', methods=['POST', 'GET'])
def changebook():
    # u = util.query_all_book()
    # MVC模式重构
    m = bookModel()
    books = m.get_all_book_data()
    return render_template("changebook.html", books=books)


# 修改书籍界面 详细界面
@app.route('/changebookinfor/<bookid>', methods=['POST', 'GET'])
def changebookinfor(bookid):
    try:
        detail = util.query_one_book_byid(bookid)
        if not detail:
            flash(f"图书ID {bookid} 不存在")
            return redirect(url_for('changebook'))
        
        if request.method == "POST":
            form = request.form
            number = (form.get('number') or '').strip()
            name = (form.get('bookname') or '').strip()
            author = (form.get('author') or '').strip()
            publicationdate = (form.get('pdate') or '').strip()
            location = (form.get('address') or '').strip()
            remark = (form.get('description') or '').strip()
            
            if not number:
                flash("请输入id")
                return render_template("changebookinfor.html", detail=detail)
            if not name:
                flash("请输入书名")
                return render_template("changebookinfor.html", detail=detail)
            if not location:
                flash("请输入位置")
                return render_template("changebookinfor.html", detail=detail)
            
            # 如果ID改变了，检查新ID是否已存在
            if number != bookid:
                existing = util.query_one_book_byid(number)
                if existing:
                    flash(f"图书ID {number} 已存在，请使用不同的ID")
                    return render_template("changebookinfor.html", detail=detail)
            
            # 先删除旧记录，再添加新记录（保持原有逻辑）
            util.delete_book(bookid)
            util.add_book(number, name, author, publicationdate, location, remark)
            
            # 重新查询更新后的数据
            detail = util.query_one_book_byid(number)
            flash("修改图书成功")
            return render_template("changebookinfor.html", detail=detail)
        else:
            return render_template("changebookinfor.html", detail=detail)
    except Exception as e:
        print(f"修改图书错误: {str(e)}")
        print(traceback.format_exc())
        flash(f"修改图书失败: {str(e)}")
        try:
            detail = util.query_one_book_byid(bookid)
            return render_template("changebookinfor.html", detail=detail)
        except:
            return redirect(url_for('changebook'))


# 查询界面
@app.route('/querybook', methods=['POST', 'GET'])
def querybook():
    # u = util.query_all_book()
    # MVC模式重构
    m = bookModel()
    books = m.get_all_book_data()
    if request.method == "POST":
        name = request.values.get('bookname')
        # onebook=util.query_one_book(name)
        # MVC模式重构
        onebook = m.get_one_book_data(name)
        return render_template("querybook.html", books=onebook, name=name, role='admin')
    else:
        return render_template("querybook.html", books=books, role='admin')


# 图书借阅信息界面
@app.route('/borrowrecord', methods=['POST', 'GET'])
def borrowrecord():
    # u = util.query_borrowrecord()
    # MVC模式重构
    m = recordModel()
    records = m.get_record_data()
    return render_template("borrowrecord.html", records=records)


# 读者信息信息界面
@app.route('/readerinfor', methods=['POST', 'GET'])
def readerinfor():
    # MVC模式重构
    m = readerModel()
    readers = m.get_reader_data()
    return render_template("readerinfor.html", readers=readers)

# 读者个人信息查看和修改
@app.route('/reader/profile', methods=['POST', 'GET'])
def reader_profile():
    """读者个人信息页面"""
    if not session.get('role') == 'reader':
        return redirect(url_for('login'))
    
    username = session.get('username') or ''
    m = readerModel()
    reader_info = m.get_reader_by_username(username)
    
    if request.method == "POST":
        try:
            form = request.form
            reader_name = (form.get('reader_name') or '').strip()
            reader_class = (form.get('reader_class') or '').strip()
            reader_learn_num = (form.get('reader_learn_num') or '').strip()
            reader_phone = (form.get('reader_phone') or '').strip()
            
            util.update_reader_info(username, reader_name, reader_class, reader_learn_num, reader_phone)
            flash("个人信息更新成功")
            # 重新获取更新后的信息
            reader_info = m.get_reader_by_username(username)
        except Exception as e:
            print(f"更新读者信息错误: {str(e)}")
            print(traceback.format_exc())
            flash(f"更新失败: {str(e)}")
    
    return render_template("reader_profile.html", reader=reader_info)

@app.route('/reader/querybook', methods=['GET', 'POST'])
def reader_querybook():
    if not session.get('role') == 'reader':
        return redirect(url_for('login'))
    if request.method == "POST":
        name = request.values.get('bookname')
        onebook = util.query_one_book(name)
        books = []
        for i in onebook:
            b = type('obj', (object,), {})()
            setattr(b, 'number', i[0])
            setattr(b, 'name', i[1])
            setattr(b, 'author', i[2])
            setattr(b, 'publicationdate', i[3])
            setattr(b, 'location', i[4])
            setattr(b, 'remark', i[5])
            setattr(b, 'isborrow', 0)
            books.append(b)
        return render_template("querybook.html", books=books, name=name, role='reader')
    else:
        rows = util.query_all_book_with_borrow()
        books = []
        for i in rows:
            b = type('obj', (object,), {})()
            setattr(b, 'number', i[0])
            setattr(b, 'name', i[1])
            setattr(b, 'author', i[2])
            setattr(b, 'publicationdate', i[3])
            setattr(b, 'location', i[4])
            setattr(b, 'remark', i[5])
            setattr(b, 'isborrow', i[6])
            books.append(b)
        return render_template("querybook.html", books=books, role='reader')

@app.route('/borrow/<bookid>', methods=['GET'])
def borrow(bookid):
    try:
        if not session.get('role') == 'reader':
            return redirect(url_for('login'))
        
        # 检查图书是否存在
        existing = util.query_one_book_byid(bookid)
        if not existing:
            flash(f"图书ID {bookid} 不存在")
            return redirect(url_for('reader_querybook'))
        
        # 检查图书是否已被借阅
        all_books = util.query_all_book_with_borrow()
        for book in all_books:
            if str(book[0]) == str(bookid) and book[6] == 1:
                flash(f"图书已被借阅，无法重复借阅")
                return redirect(url_for('reader_querybook'))
        
        from datetime import datetime
        username = session.get('username') or ''
        
        # 获取读者姓名（从读者信息表）
        try:
            reader_info = util.query_reader_by_username(username)
            if reader_info:
                borrowname = reader_info[1]  # name字段
            else:
                borrowname = username  # 如果没有读者信息，使用用户名
        except:
            borrowname = username
        
        util.borrow_book(bookid, borrowname, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username)
        flash("借阅成功")
        return redirect(url_for('reader_querybook'))
    except Exception as e:
        print(f"借阅图书错误: {str(e)}")
        print(traceback.format_exc())
        flash(f"借阅失败: {str(e)}")
        return redirect(url_for('reader_querybook'))

@app.route('/return/<bookid>', methods=['GET'])
def return_book_route(bookid):
    try:
        if not session.get('role') == 'reader':
            return redirect(url_for('login'))
        
        username = session.get('username') or ''
        
        # 检查图书是否存在
        existing = util.query_one_book_byid(bookid)
        if not existing:
            flash(f"图书ID {bookid} 不存在")
            return redirect(url_for('reader_querybook'))
        
        # 检查是否是当前用户借阅的图书
        all_books = util.query_all_book_with_borrow()
        for book in all_books:
            if str(book[0]) == str(bookid):
                # 这里需要检查借阅人，但当前数据结构可能不支持，先简单处理
                if book[6] == 0:
                    flash("该图书未被借阅，无需归还")
                    return redirect(url_for('reader_querybook'))
                break
        
        username = session.get('username') or ''
        util.return_book(bookid, username)
        flash("归还成功")
        return redirect(url_for('reader_querybook'))
    except Exception as e:
        print(f"归还图书错误: {str(e)}")
        print(traceback.format_exc())
        flash(f"归还失败: {str(e)}")
        return redirect(url_for('reader_querybook'))

@app.route('/recommend', methods=['GET'])
def recommend():
    if not session.get('role') == 'reader':
        return redirect(url_for('login'))
    username = session.get('username') or ''
    rows = util.query_borrowrecord()
    prefer_authors = []
    prefer_words = []
    for r in rows:
        if str(r[3]) == username:
            bid = r[0]
            one = util.query_one_book_byid(str(bid))
            for i in one:
                if i[2]:
                    prefer_authors.append(i[2])
                if i[5]:
                    for w in str(i[5]).replace('，', ' ').replace(',', ' ').split():
                        if len(w) > 1:
                            prefer_words.append(w.lower())
    llm_url = os.environ.get('LLM_API_URL', '')
    llm_key = os.environ.get('LLM_API_KEY', '')
    llm_model = os.environ.get('LLM_MODEL', 'gpt-4o-mini')
    use_llm = bool(llm_url and llm_key)
    if use_llm:
        try:
            payload = {
                "model": llm_model,
                "messages": [
                    {"role": "system", "content": "你是图书推荐助手。请根据读者的偏好返回JSON，包含authors和keywords两个数组。"},
                    {"role": "user", "content": json.dumps({"authors": prefer_authors, "keywords": prefer_words}, ensure_ascii=False)}
                ],
                "response_format": {"type": "json_object"}
            }
            req = urllib.request.Request(llm_url, data=json.dumps(payload).encode('utf-8'))
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', 'Bearer ' + llm_key)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read().decode('utf-8')
                obj = json.loads(data)
                content = obj.get('choices', [{}])[0].get('message', {}).get('content', '{}')
                parsed = json.loads(content)
                rec_authors = parsed.get('authors', [])
                rec_keywords = parsed.get('keywords', [])
        except Exception:
            rec_authors = prefer_authors
            rec_keywords = prefer_words
    else:
        rec_authors = prefer_authors
        rec_keywords = prefer_words
    allrows = util.query_all_book()
    scored = []
    for i in allrows:
        score = 0
        if i[2] in rec_authors:
            score += 2
        if i[5]:
            remark_l = str(i[5]).lower()
            for w in rec_keywords:
                if w in remark_l:
                    score += 1
        if score > 0:
            scored.append((score, i))
    scored.sort(key=lambda x: x[0], reverse=True)
    books = []
    for _, i in scored[:20]:
        b = type('obj', (object,), {})()
        setattr(b, 'number', i[0])
        setattr(b, 'name', i[1])
        setattr(b, 'author', i[2])
        setattr(b, 'publicationdate', i[3])
        setattr(b, 'location', i[4])
        setattr(b, 'remark', i[5])
        setattr(b, 'isborrow', 0)
        books.append(b)
    return render_template("querybook.html", books=books, role='reader')

@app.route('/chat', methods=['POST'])
def chat():
    """智能问答接口，支持读者和管理员"""
    try:
        # 获取用户消息
        msg = ''
        data = request.get_json(silent=True)
        if data and isinstance(data, dict):
            msg = str(data.get('message') or '').strip()
        if not msg:
            msg = (request.values.get('message') or '').strip()
        
        if not msg:
            return jsonify({"reply": "请先输入你的问题。"}), 400
        
        # 获取当前用户角色
        user_role = session.get('role', 'reader')
        username = session.get('username', '')
        
        # 获取所有图书数据作为上下文
        try:
            allrows = util.query_all_book()
        except Exception as e:
            print(f"查询图书数据失败: {str(e)}")
            allrows = []
        
        # 提取关键词用于搜索相关图书
        terms = []
        for x in re.split(r'[\s,，。；;、]+', msg):
            x = x.strip().lower()
            if len(x) > 1:
                terms.append(x)
        
        # 根据关键词匹配相关图书
        scored = []
        for i in allrows:
            score = 0
            name_l = str(i[1] or '').lower()
            author_l = str(i[2] or '').lower()
            remark_l = str(i[5] or '').lower()
            for w in terms:
                if w and (w in name_l or w in author_l or w in remark_l):
                    score += 1
            if score > 0 or not terms:
                scored.append((score, i))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        top = [x[1] for x in scored[:20]]
        
        # 构建上下文数据
        context_list = []
        for i in top:
            context_list.append({
                "id": i[0],
                "name": i[1] or '',
                "author": i[2] or '',
                "publicationdate": i[3] or '',
                "location": i[4] or '',
                "remark": i[5] or ''
            })
        
        # 如果是管理员，添加更多上下文信息
        if user_role == 'admin':
            try:
                # 添加借阅记录统计
                borrow_records = util.query_borrowrecord()
                context_list.append({
                    "_meta": {
                        "total_books": len(allrows),
                        "borrowed_books": len(borrow_records),
                        "available_books": len(allrows) - len(borrow_records)
                    }
                })
            except Exception:
                pass
        
        # 使用DeepSeek服务获取回复
        api_available = False
        api_error_reason = None
        try:
            deepseek = get_deepseek_service()
            if deepseek.is_available():
                api_available = True
                reply = deepseek.chat(msg, context=context_list, role=user_role)
                # 如果返回了有效回复（不是None）
                if reply:
                    return jsonify({"reply": reply})
                else:
                    # reply为None，说明API调用失败，需要降级
                    # 检查是否是余额不足（通过检查控制台输出或错误信息）
                    # 由于deepseek_service已经打印了错误信息，我们设置一个通用错误原因
                    api_error_reason = "API调用失败"
                    print("DeepSeek API返回None，将使用降级方案")
            else:
                # API未配置
                api_error_reason = "未配置"
                print("DeepSeek API未配置，使用关键词匹配")
        except Exception as e:
            error_str = str(e)
            # 检查异常信息中是否包含余额不足
            if "Insufficient Balance" in error_str or "余额不足" in error_str or "insufficient" in error_str.lower():
                api_error_reason = "余额不足"
            else:
                api_error_reason = f"异常: {error_str}"
            print(f"DeepSeek服务调用异常: {error_str}")
            print(traceback.format_exc())
            # 继续执行降级方案
        
        # 如果DeepSeek不可用或失败，使用简单的关键词匹配回复
        fallback_hint = ""
        if api_available:
            if "Insufficient Balance" in str(api_error_reason) or "余额不足" in str(api_error_reason):
                fallback_hint = "\n\n提示：DeepSeek API余额不足，当前使用关键词匹配功能。如需使用智能问答，请充值API账户。"
            elif api_error_reason:
                fallback_hint = f"\n\n提示：DeepSeek API暂时不可用({api_error_reason})，当前使用关键词匹配功能。"
            else:
                fallback_hint = "\n\n提示：DeepSeek API暂时不可用，当前使用关键词匹配功能。"
        else:
            fallback_hint = "\n\n提示：DeepSeek API未配置，当前使用关键词匹配功能。如需使用智能问答，请配置API密钥。"
        
        if top:
            lines = []
            for i in top[:10]:
                lines.append(f"编号：{i[0]} | 书名：{i[1]} | 作者：{i[2]}")
            return jsonify({
                "reply": "为你找到相关图书：\n" + "\n".join(lines) + fallback_hint
            })
        
        return jsonify({
            "reply": "未找到匹配的书籍。可以尝试使用书名、作者或关键词搜索。" + fallback_hint
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"聊天接口错误: {error_msg}")
        print(traceback.format_exc())
        # 返回详细的错误信息以便调试
        return jsonify({
            "reply": f"系统出现错误: {error_msg}。请检查控制台日志获取详细信息。"
        }), 500


# 错误界面（异常处理）
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


if __name__ == '__main__':
    app.run(debug=True)
