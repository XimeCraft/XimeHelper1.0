from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/restaurants')
def get_restaurants():
    page = int(request.args.get('page', 1))
    # 模拟数据库分页
    restaurants = [
        {
            'name': f'Xiao Cafe {i}',
            'image': 'https://via.placeholder.com/300x200',
            'price': '$20-30',
            'time': '20 minutes'
        }
        for i in range((page-1)*12, page*12)  # 每页12个餐厅
    ]
    
    return jsonify({
        'restaurants': restaurants,
        'has_more': True  # 可以根据实际数据判断是否还有更多
    })

if __name__ == '__main__':
    app.run(debug=True)