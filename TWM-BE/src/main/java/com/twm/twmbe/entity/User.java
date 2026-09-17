// User.java
package com.twm.twmbe.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Table(name = "user")
@Data
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String username;

    private String password;
    private String nickname;
    private String avatar;
    private String bio;
    private String gender;
    private String birthday;
    private String phone;
    private String email;

    @Column(columnDefinition = "TEXT")
    private String location; // JSON格式存储

    @Column(name = "preferred_travel_types", columnDefinition = "TEXT")
    private String preferredTravelTypes; // JSON格式存储

    @Column(name = "frequent_destinations", length = 500)
    private String frequentDestinations;

    @Column(name = "social_links", columnDefinition = "TEXT")
    private String socialLinks; // JSON格式存储

    @Column(name = "follow_count")
    private Integer followCount = 0;

    @Column(name = "fans_count")
    private Integer fansCount = 0;

    @Column(name = "like_count")
    private Integer likeCount = 0;

    @Column(name = "post_count")
    private Integer postCount = 0;

    @Column(name = "collection_count")
    private Integer collectionCount = 0;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(name = "updated_at")
    private LocalDateTime updatedAt = LocalDateTime.now();

    // 统计字段（非数据库字段）
    @Transient
    private Integer browseHistoryCount = 0;
}