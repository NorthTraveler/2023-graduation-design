from flask import Flask,render_template,request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import datetime
from method import fororderID,UrgentCount

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:wh13213682290@localhost:3306/forgd?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
db = SQLAlchemy(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


class Production(db.Model):
    __tablename__ = "production"
    ProductionID = db.Column(db.String(45) , primary_key = True , autoincrement=True)
    ProductionCode = db.Column(db.String(45))
    Department = db.Column(db.String(45))

class Management(db.Model):
    __tablename__ = "management"
    ManagementID = db.Column(db.String(45), primary_key = True , autoincrement =True)
    ManagementCode = db.Column(db.String(45))
    ManagementName = db.Column(db.String(45))

class WaitingOrders(db.Model):
    __tablename__ = "waitingorders"
    Name = db.Column(db.String(45),primary_key = True)
    Number = db.Column(db.String(45))
    Deadline = db.Column(db.String(45))

class ProductionOrders(db.Model):
    __tablename__ = "productionorders"
    OrdersID = db.Column(db.String(45),primary_key =True,index = True)
    ReceiveTime = db.Column(db.String(45))
    Name = db.Column(db.String(45))
    Number = db.Column(db.String(45))
    Status = db.Column(db.String(45),index = True)
    Remark = db.Column(db.String(45),default = "暂无备注")
    Deadline = db.Column(db.String(45))
    Urgent = db.Column(db.String(45))

class CompletedOrders(db.Model):
    __tablename__ = "completedorders"
    OrdersID = db.Column(db.String(45),primary_key = True ,index = True)
    ReceiveTime = db.Column(db.String(45))
    Name = db.Column(db.String(45))
    Number = db.Column(db.String(45))
    SubmissionTime = db.Column(db.String(45))
    Deadline = db.Column(db.String(45))
    Status = db.Column(db.String(45))

#主页面
@app.route('/', methods=['GET','POST'])
def Mainpage():
    Production_Orders = ProductionOrders.query.order_by(ProductionOrders.Urgent.desc()).limit(5)
    return render_template('MainPage.html',Production_orders = Production_Orders )



#管理人员登录
@app.route('/ManagementLogin' , methods=['GET','POST'])
def ManagementLogin():
    if request.method =='POST':
        ManagementID = request.form['ManagementID']
        ManagementCode = request.form['ManagementCode']
        management = Management.query.filter_by(ManagementID = ManagementID).first()
        if management:
            if management.ManagementID == ManagementID and management.ManagementCode == ManagementCode:
                return redirect(url_for('OrderReceive'))
            else:
                error = '无效的管理人员编号或密码，请重试！'
                return render_template('ManagementLogin.html', message=error)
        else:
            error = '无效的管理人员编号或密码，请重试！'
            return render_template('ManagementLogin.html', message=error)
    return render_template('ManagementLogin.html')
    #     Managements = Management.query.all()
    #     for management in Managements:
    #         if management.ManagementID == ManagementID and management.ManagementCode == ManagementCode:
    #             flash("欢迎使用本订单系统，管理员", category="info")
    #             return redirect(url_for('OrderReceive'))
    #         flash('无效的管理员编号或密码，请重试！')
    #     return render_template('ManagementLogin.html')
    # else:
    #     return render_template('ManagementLogin.html')


#生产人员登录
@app.route('/ProductionLogin',methods=['GET','POST'])
def ProductionLogin():
    if request.method == 'POST':
        ProductionID = request.form['ProductionID']
        ProductionCode = request.form['ProductionCode']
        # PIDCode = Production.query.filter_by(ProductionID == ProductionID)
        production = Production.query.filter_by(ProductionID=ProductionID).first()
        if production:
            if production.ProductionID == ProductionID and production.ProductionCode == ProductionCode:
                return redirect(url_for('production', department=production.Department))
            else:
                error = '无效的生产部门编号或密码，请重试！'
                return render_template('ProductionLogin.html', message=error)
        else:
            error = '无效的生产部门编号或密码，请重试！'
            return render_template('ProductionLogin.html', message=error)
    return render_template('ProductionLogin.html')
    #     Productions = Production.query.all()
    #     for production in Productions:
    #         if production.ProductionID == ProductionID and production.ProductionCode == ProductionCode:
    #             return redirect(url_for('production', department=production.Department))
    #     error = '无效的生产部门编号或密码，请重试！'
    #     return render_template('ProductionLogin.html', message=error)
    # else:
    #     return render_template('ProductionLogin.html')


@app.route('/OrderEnter',methods = ['GET','POST'])
def OrderEnter():
    if request.method == 'POST':
        Name = request.form.get('Name')
        Number = request.form.get('Number')
        Deadline = request.form.get('Deadline')
        NewReceiveOrder = WaitingOrders(Name = Name,Number = Number, Deadline = Deadline)
        db.session.add(NewReceiveOrder)
        db.session.commit()
        return render_template('/OrderEnter.html')
    return render_template('/OrderEnter.html')

@app.route('/OrderReceive',methods=['GET','POST'])
def OrderReceive():
    Waiting_orders = WaitingOrders.query.all()
    if request.method == 'POST':
        N=request.form.get('Number')
        OrderID = fororderID(N)
        ReceiveTime = datetime.datetime.now().date()
        Name = request.form.get('Name')
        Status = "design"
        Remark = "None"
        Deadline = request.form.get('Deadline')
        Urgent = UrgentCount(ReceiveTime,N,Deadline)
        NewProducutionOrder = ProductionOrders(OrdersID = OrderID,ReceiveTime = ReceiveTime,Name = Name,Number = N,Status= Status,Remark= Remark,Deadline=Deadline,Urgent=Urgent)
        db.session.add(NewProducutionOrder)
        result = WaitingOrders.query.get(Name)
        if result:
            db.session.delete(result)
        db.session.commit()
        Waiting_orders = WaitingOrders.query.all()
    return render_template('/OrderReceive.html',waiting_orders = Waiting_orders)

@app.route('/OrderList',methods = ['GET','POST'])
def OrderList():
    Production_orders = ProductionOrders.query.order_by(ProductionOrders.Urgent.desc()).all()
    if request.method == 'POST':
        OrdersID = request.form.get('OrdersID')
        return redirect(url_for('OrderDetail', OrdersID = OrdersID))
    return render_template('/OrderList.html', Production_orders = Production_orders)

@app.route('/OrderFinsh',methods = ['GET','POST'])
def OrderFinsh():
    Completed_orders =CompletedOrders.query.order_by(CompletedOrders.SubmissionTime).all()
    if request.method == 'POST':
        OrdersID = request.form.get('OrdersID')
        return redirect(url_for('OrderDetail', OrdersID = OrdersID))
    return render_template('/OrderFinsh.html', Completed_orders = Completed_orders)

@app.route('/OrderManage/<string:OrdersID>', methods=['GET','POST'])
def OrderManage(OrdersID):
    Production_orders = ProductionOrders.query.get(OrdersID)
    if request.method == 'POST':
        Name = request.form.get('Name')
        Number = request.form.get('Number')
        Status = request.form.get('Status')
        Remark = request.form.get('Remark')
        Deadline = request.form.get('Deadline')
        Order = ProductionOrders.query.filter_by(OrdersID=OrdersID).first()
        Order.Name = Name
        Order.Number = Number
        Order.Status = Status
        Order.Remark = Remark
        Order.Deadline = Deadline
        db.session.commit()
        return render_template('/OrderManage.html',production_order = Production_orders)
    return render_template('/OrderManage.html',production_order = Production_orders)

@app.route('/OrderSend',methods=['GET','POST'])
def OrderSend():
    Order = ProductionOrders.query.filter(ProductionOrders.Status == "completed")
    if request.method == 'POST':
        OrdersID = request.form.get('OrdersID')
        ReceiveTime = request.form.get('ReceiveTime')
        Name = request.form.get('Name')
        Number = request.form.get('Number')
        Deadline = request.form.get('Deadline')
        SubmissionTime = datetime.datetime.now().date()
        if 'send' in request.form:
            Status ='已发送'
        elif 'storage' in request.form:
            Status = '已入库'
        NewCompletedOrder = CompletedOrders(OrdersID = OrdersID, ReceiveTime = ReceiveTime, Name = Name, Number = Number, SubmissionTime = SubmissionTime, Deadline = Deadline,Status = Status)
        print(NewCompletedOrder)
        db.session.add(NewCompletedOrder)
        result = ProductionOrders.query.get(OrdersID)
        print(result)
        if result:
            db.session.delete(result)
        db.session.commit()
        return render_template('/OrderSend.html',completed_orders = Order)
    return render_template('/OrderSend.html',completed_orders = Order)



@app.route('/OrderDetail/<string:OrdersID>',methods=['GET','POST'])
def OrderDetail(OrdersID):
    Order = ProductionOrders.query.filter(ProductionOrders.OrdersID == OrdersID ).first()
    if Order:
        Order = Order
    else:
        Order = CompletedOrders.query.filter(CompletedOrders.OrdersID == OrdersID).first()
    if request.method == 'POST':
        OrdersID = Order.OrdersID
        Order1 = ProductionOrders.query.filter_by(OrdersID=OrdersID).first()
        if Order1:
            Urgent1 = eval(Order.Urgent) + 100
            Order1.Urgent = Urgent1
            db.session.commit()
    return render_template('/OrderDetail.html',Order = Order)

# 生产部门任务接受
@app.route('/Production/<string:department>',methods=['GET','POST'])
def production(department):
    Production_orders = ProductionOrders.query.order_by(ProductionOrders.Urgent.desc()).all()
    order_list = []
    Urgent_Production_orders=[]
    for order in Production_orders:
        if order.Status == department:
            order_list.append(order)
    for order1 in order_list:
        if eval(order1.Urgent) > 10:
            Urgent_Production_orders.append(order1)
    if department == "design":
        departmentname = "设计部门"
    elif department == "process":
        departmentname = "加工部门"
    elif department == "refine":
        departmentname = "精修部门"
    elif department == "examine":
        departmentname = "核验部门"
    if request.method == 'POST':
        ID = request.form.get('OrdersID')
        print(ID)
        Status = department+"ing"
        print(Status)
        Order = ProductionOrders.query.filter_by(OrdersID=ID).first()
        Order.Status = Status
        db.session.commit()
    return render_template('/Production.html' , department=department, orders=order_list,departmentname=departmentname, Urgent_Production_orders=Urgent_Production_orders)

# 生产部门任务提交
@app.route('/Submit/<string:department>',methods=['GET','POST'])
def Submit(department):
    Production_orders = ProductionOrders.query.order_by(ProductionOrders.Urgent.desc()).all()
    order_list = []
    Department=department+"ing"
    for order in Production_orders:
        if order.Status == Department:
            order_list.append(order)
    if request.method == 'POST':
        ID = request.form.get('OrdersID')
        Order = ProductionOrders.query.filter_by(OrdersID=ID).first()
        Status = None
        if Order.Status == "designing":
            Status = "process"
        elif Order.Status == "processing":
            Status = "refine"
        elif Order.Status == "refineing":
            Status = "examine"
        elif Order.Status == "examineing":
            Status = "completed"
        if Status:
            Order.Status = Status
        db.session.commit()

        return render_template('/Submit.html', department=department, orders=order_list)
    return render_template('/Submit.html' , department = department, orders=order_list)
# @app.route('/OrderList',method=['GET','POST'])
@app.route('/Search',methods=['GET','POST'])
def Search():
    if request.method == 'POST':
        ID = request.form['ID']
        if ID:
            orders = ProductionOrders.query.filter(ProductionOrders.OrdersID.like(f'%{ID}%')).all()
            Corders = CompletedOrders.query.filter(CompletedOrders.OrdersID.like(f'%{ID}%')).all()
            return render_template('/Search.html', orders=orders,Corders = Corders)
    return render_template('/Search.html')

#显示每天完成的任务量
@app.route('/OrderChart',methods=['GET','POST'])
def OrderChart():
    today = datetime.datetime.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    yyesterday = yesterday - oneday
    Waiting_Orders = WaitingOrders.query.count()
    Production_Orders = ProductionOrders.query.count()
    receive_order = ProductionOrders.query.filter_by(ReceiveTime = today).count()
    receive_order_yesterday = ProductionOrders.query.filter_by(ReceiveTime = yesterday).count()
    receive_order_yyesterday = ProductionOrders.query.filter_by(ReceiveTime=yyesterday).count()
    sub_order = CompletedOrders.query.filter_by(SubmissionTime = today).count()
    sub_order1 = CompletedOrders.query.filter_by(SubmissionTime = yesterday).count()
    sub_order2 = CompletedOrders.query.filter_by(SubmissionTime = yyesterday).count()
    return  render_template('/OrderChart.html', Waiting_Orders = Waiting_Orders,Production_Orders = Production_Orders,receive_order = receive_order,receive_order_yesterday= receive_order_yesterday,receive_order_yyesterday =receive_order_yyesterday,sub_order = sub_order,sub_order1=sub_order1,sub_order2=sub_order2)

if __name__ == '__main__':
    app.run()
