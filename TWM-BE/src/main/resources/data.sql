-- 插入测试帖子数据（如果表中没有数据）
INSERT IGNORE INTO post (id, title, content, image_urls, location, user_id, view_count, like_count, comment_count, created_at, updated_at) VALUES
                                                                                                                                               (1, '旅行日记：云南之旅', '这次去了云南，看到了美丽的洱海和玉龙雪山，非常震撼。云南的气候宜人，风景如画，是一个值得多次游览的地方。',
                                                                                                                                                'https://example.com/image1.jpg,https://example.com/image2.jpg', '云南大理', 1, 156, 23, 8, '2024-01-15 10:30:00', '2024-01-15 10:30:00'),

                                                                                                                                               (2, '日本京都的樱花', '春天在京都赏樱，感受到了日本文化的独特魅力。樱花盛开的季节，整个城市都变成了粉色的海洋，美不胜收。',
                                                                                                                                                'https://example.com/image3.jpg,https://example.com/image4.jpg', '日本京都', 2, 289, 45, 12, '2024-01-14 14:20:00', '2024-01-14 14:20:00'),

                                                                                                                                               (3, '海边露营体验', '在海边露营，听着海浪声入睡，非常治愈。清晨看着太阳从海平面升起，感觉所有的烦恼都消失了。',
                                                                                                                                                'https://example.com/image5.jpg,https://example.com/image6.jpg', '青岛海滩', 3, 198, 34, 15, '2024-01-13 18:45:00', '2024-01-13 18:45:00'),

                                                                                                                                               (4, '西藏自驾游', '完成了西藏自驾之旅，沿途的风景让人震撼。高原的蓝天白云，还有虔诚的信仰，都让人印象深刻。',
                                                                                                                                                'https://example.com/image7.jpg,https://example.com/image8.jpg', '西藏拉萨', 1, 324, 67, 23, '2024-01-12 09:15:00', '2024-01-12 09:15:00'),

                                                                                                                                               (5, '成都美食探索', '成都真的是美食天堂！从火锅到串串，从担担面到龙抄手，每一道菜都让人回味无穷。',
                                                                                                                                                'https://example.com/image9.jpg,https://example.com/image10.jpg', '四川成都', 2, 142, 28, 6, '2024-01-11 16:30:00', '2024-01-11 16:30:00');