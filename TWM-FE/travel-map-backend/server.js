// server.js
const express = require('express');
const mysql = require('mysql2/promise');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

// 数据库连接配置 - 使用您的MySQL 8.0配置
const dbConfig = {
    host: 'localhost',
    user: 'root',
    password: '123456',
    database: 'twm',
    charset: 'utf8mb4'
};

// 创建数据库连接池
const pool = mysql.createPool(dbConfig);

// 测试数据库连接
async function testConnection() {
    try {
        const connection = await pool.getConnection();
        console.log('✅ 数据库连接成功');
        connection.release();
    } catch (error) {
        console.error('❌ 数据库连接失败:', error.message);
    }
}

testConnection();

// 错误处理中间件
app.use((error, req, res, next) => {
    console.error('Error:', error);
    res.status(500).json({ 
        success: false, 
        message: '服务器内部错误' 
    });
});

// 初始化数据库表
app.get('/api/init-db', async (req, res) => {
    const connection = await pool.getConnection();
    
    try {
        await connection.beginTransaction();
        
        // 创建表结构
        const tables = [
            `CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                openid VARCHAR(100) UNIQUE,
                nickname VARCHAR(100),
                avatar_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )`,
            
            `CREATE TABLE IF NOT EXISTS locations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                address VARCHAR(500),
                latitude DECIMAL(10, 6) NOT NULL,
                longitude DECIMAL(10, 6) NOT NULL,
                type ENUM('attraction', 'hotel', 'food', 'shopping', 'default'),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_location (latitude, longitude)
            )`,
            
            `CREATE TABLE IF NOT EXISTS routes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                transport_type ENUM('walk', 'bike', 'bus', 'drive'),
                total_distance DECIMAL(8,2),
                estimated_time INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )`,
            
            `CREATE TABLE IF NOT EXISTS route_locations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                route_id INT,
                location_id INT,
                sort_order INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (route_id) REFERENCES routes(id),
                FOREIGN KEY (location_id) REFERENCES locations(id),
                UNIQUE KEY unique_route_location (route_id, location_id, sort_order)
            )`
        ];
        
        for (const tableSql of tables) {
            await connection.execute(tableSql);
        }
        
        // 插入一些示例数据
        const sampleLocations = [
            ['故宫博物院', '北京市东城区景山前街4号', 39.918, 116.397, 'attraction'],
            ['天安门广场', '北京市东城区东长安街', 39.909, 116.397, 'attraction'],
            ['王府井大街', '北京市东城区王府井大街', 39.914, 116.417, 'shopping'],
            ['颐和园', '北京市海淀区新建宫门路19号', 39.999, 116.273, 'attraction'],
            ['鸟巢', '北京市朝阳区国家体育场南路1号', 39.993, 116.396, 'attraction']
        ];
        
        for (const location of sampleLocations) {
            await connection.execute(
                'INSERT IGNORE INTO locations (name, address, latitude, longitude, type) VALUES (?, ?, ?, ?, ?)',
                location
            );
        }
        
        await connection.commit();
        
        res.json({
            success: true,
            message: '数据库初始化成功'
        });
    } catch (error) {
        await connection.rollback();
        console.error('数据库初始化失败:', error);
        res.status(500).json({
            success: false,
            message: '数据库初始化失败: ' + error.message
        });
    } finally {
        connection.release();
    }
});

// 搜索地点API
app.get('/api/locations/search', async (req, res) => {
    try {
        const { keyword, latitude, longitude, radius = 10 } = req.query;
        
        if (!keyword) {
            return res.status(400).json({
                success: false,
                message: '搜索关键词不能为空'
            });
        }
        
        let sql = `
            SELECT id, name, address, latitude, longitude, type,
            (6371 * acos(cos(radians(?)) * cos(radians(latitude)) * 
            cos(radians(longitude) - radians(?)) + sin(radians(?)) * 
            sin(radians(latitude)))) AS distance
            FROM locations 
            WHERE name LIKE ? OR address LIKE ?
        `;
        
        let params = [
            latitude || 39.909, longitude || 116.397, latitude || 39.909,
            `%${keyword}%`, `%${keyword}%`
        ];
        
        if (radius) {
            sql += ' HAVING distance < ? ORDER BY distance LIMIT 20';
            params.push(parseFloat(radius));
        } else {
            sql += ' ORDER BY distance LIMIT 20';
        }
        
        const [results] = await pool.execute(sql, params);
        
        res.json({
            success: true,
            data: results
        });
    } catch (error) {
        console.error('搜索地点失败:', error);
        res.status(500).json({
            success: false,
            message: '搜索失败'
        });
    }
});

// 添加新地点API
app.post('/api/locations', async (req, res) => {
    try {
        const { name, address, latitude, longitude, type = 'default' } = req.body;
        
        // 验证必填字段
        if (!name || !latitude || !longitude) {
            return res.status(400).json({
                success: false,
                message: '地点名称和坐标是必填项'
            });
        }
        
        const sql = `
            INSERT INTO locations (name, address, latitude, longitude, type)
            VALUES (?, ?, ?, ?, ?)
        `;
        
        const [result] = await pool.execute(sql, [
            name, address, latitude, longitude, type
        ]);
        
        res.json({
            success: true,
            data: {
                id: result.insertId,
                name,
                address,
                latitude,
                longitude,
                type
            },
            message: '地点添加成功'
        });
    } catch (error) {
        console.error('添加地点失败:', error);
        res.status(500).json({
            success: false,
            message: '添加地点失败: ' + error.message
        });
    }
});

// 保存路线API
app.post('/api/routes', async (req, res) => {
    const connection = await pool.getConnection();
    
    try {
        await connection.beginTransaction();
        
        const { userId, name, description, transportType, locations } = req.body;
        
        // 1. 创建路线
        const routeSql = `
            INSERT INTO routes (user_id, name, description, transport_type)
            VALUES (?, ?, ?, ?)
        `;
        
        const [routeResult] = await connection.execute(routeSql, [
            userId, name, description, transportType
        ]);
        
        const routeId = routeResult.insertId;
        
        // 2. 添加路线地点关联
        for (let i = 0; i < locations.length; i++) {
            const location = locations[i];
            
            // 如果地点不存在，先创建地点
            let locationId = location.id;
            if (!locationId || locationId > 1000) { // 新添加的地点
                const locationSql = `
                    INSERT INTO locations (name, latitude, longitude, type, address)
                    VALUES (?, ?, ?, ?, ?)
                `;
                const [locResult] = await connection.execute(locationSql, [
                    location.name, location.latitude, location.longitude, 
                    location.type || 'default', location.address || ''
                ]);
                locationId = locResult.insertId;
            }
            
            // 关联路线和地点
            const routeLocationSql = `
                INSERT INTO route_locations (route_id, location_id, sort_order)
                VALUES (?, ?, ?)
            `;
            await connection.execute(routeLocationSql, [routeId, locationId, i + 1]);
        }
        
        await connection.commit();
        
        res.json({
            success: true,
            data: { routeId },
            message: '路线保存成功'
        });
    } catch (error) {
        await connection.rollback();
        console.error('保存路线失败:', error);
        res.status(500).json({
            success: false,
            message: '保存路线失败: ' + error.message
        });
    } finally {
        connection.release();
    }
});

// 获取用户路线列表API
app.get('/api/users/:userId/routes', async (req, res) => {
    try {
        const { userId } = req.params;
        
        const sql = `
            SELECT r.*, 
                   COUNT(rl.id) as location_count
            FROM routes r
            LEFT JOIN route_locations rl ON r.id = rl.route_id
            WHERE r.user_id = ?
            GROUP BY r.id
            ORDER BY r.updated_at DESC
        `;
        
        const [results] = await pool.execute(sql, [userId]);
        
        res.json({
            success: true,
            data: results
        });
    } catch (error) {
        console.error('获取路线列表失败:', error);
        res.status(500).json({
            success: false,
            message: '获取路线列表失败'
        });
    }
});

// 获取路线详情API
app.get('/api/routes/:routeId', async (req, res) => {
    try {
        const { routeId } = req.params;
        
        const sql = `
            SELECT r.*, 
                   l.id as location_id, l.name as location_name, 
                   l.latitude, l.longitude, l.type, l.address,
                   rl.sort_order
            FROM routes r
            JOIN route_locations rl ON r.id = rl.route_id
            JOIN locations l ON rl.location_id = l.id
            WHERE r.id = ?
            ORDER BY rl.sort_order
        `;
        
        const [results] = await pool.execute(sql, [routeId]);
        
        if (results.length === 0) {
            return res.status(404).json({
                success: false,
                message: '路线不存在'
            });
        }
        
        // 格式化返回数据
        const route = {
            id: results[0].id,
            name: results[0].name,
            description: results[0].description,
            transport_type: results[0].transport_type,
            locations: results.map(row => ({
                id: row.location_id,
                name: row.location_name,
                latitude: row.latitude,
                longitude: row.longitude,
                type: row.type,
                address: row.address
            }))
        };
        
        res.json({
            success: true,
            data: route
        });
    } catch (error) {
        console.error('获取路线详情失败:', error);
        res.status(500).json({
            success: false,
            message: '获取路线详情失败'
        });
    }
});

// 获取附近推荐地点API
app.get('/api/locations/nearby', async (req, res) => {
    try {
        const { latitude, longitude, radius = 5, limit = 10 } = req.query;
        
        const currentLat = latitude || 39.909;
        const currentLng = longitude || 116.397;
        
        const sql = `
            SELECT id, name, address, latitude, longitude, type,
            (6371 * acos(cos(radians(?)) * cos(radians(latitude)) * 
            cos(radians(longitude) - radians(?)) + sin(radians(?)) * 
            sin(radians(latitude)))) AS distance
            FROM locations 
            HAVING distance < ? 
            ORDER BY distance 
            LIMIT ?
        `;
        
        const [results] = await pool.execute(sql, [
            currentLat, currentLng, currentLat, 
            parseFloat(radius), parseInt(limit)
        ]);
        
        res.json({
            success: true,
            data: results
        });
    } catch (error) {
        console.error('获取附近地点失败:', error);
        res.status(500).json({
            success: false,
            message: '获取附近地点失败'
        });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 服务器运行在 http://localhost:${PORT}`);
    console.log(`📊 数据库: ${dbConfig.database}@${dbConfig.host}`);
});