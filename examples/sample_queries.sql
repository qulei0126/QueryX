-- 示例查询文件
-- 这些查询可以在QueryX工具中使用

-- 基本查询：查询所有员工数据
SELECT * FROM sample_data;

-- 条件查询：查询工资大于12000的员工
SELECT name, age, city, salary 
FROM sample_data 
WHERE salary > 12000;

-- 排序查询：按年龄升序排列
SELECT * FROM sample_data 
ORDER BY age ASC;

-- 分组查询：按城市分组统计平均工资
SELECT city, AVG(salary) as avg_salary, COUNT(*) as employee_count 
FROM sample_data 
GROUP BY city;

-- 产品查询示例
-- 查询所有产品
SELECT * FROM products;

-- 按类别分组查询产品数量和平均价格
SELECT category, COUNT(*) as product_count, AVG(price) as avg_price 
FROM products 
GROUP BY category;

-- 查询库存少于100的产品
SELECT name, category, price, stock 
FROM products 
WHERE stock < 100;

-- 订单查询示例
-- 查询所有订单
SELECT * FROM orders;

-- 查询总价超过3000的订单
SELECT order_id, customer_name, product, quantity, price, total 
FROM orders 
WHERE total > 3000;

-- 按状态分组统计订单
SELECT status, COUNT(*) as order_count, SUM(total) as total_sales 
FROM orders 
GROUP BY status;

-- 多表联合查询示例
-- 联合查询订单和产品
SELECT o.order_id, o.customer_name, p.name as product_name, 
       o.quantity, o.price, o.total, p.stock as remaining_stock
FROM orders o JOIN products p ON o.product = p.name;

-- 复杂查询：查询每个城市最高工资的员工
SELECT s1.* 
FROM sample_data s1
JOIN (
    SELECT city, MAX(salary) as max_salary 
    FROM sample_data 
    GROUP BY city
) s2 ON s1.city = s2.city AND s1.salary = s2.max_salary; 