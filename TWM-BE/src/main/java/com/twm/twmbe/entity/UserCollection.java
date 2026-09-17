// UserCollection.java
package com.twm.twmbe.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Table(name = "user_collection")
@Data
public class UserCollection {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "post_id", nullable = false)
    private Long postId;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    // 关联的帖子信息（非数据库字段）
    @Transient
    private Post post;

    public UserCollection() {}

    public UserCollection(Long userId, Long postId) {
        this.userId = userId;
        this.postId = postId;
    }
}