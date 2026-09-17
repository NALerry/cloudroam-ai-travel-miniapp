package com.twm.twmbe.repository;

import com.twm.twmbe.entity.UserLike;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserLikeRepository extends JpaRepository<UserLike, Long> {

    // 根据用户ID查找点赞记录，按创建时间倒序
    Page<UserLike> findByUserIdOrderByCreatedAtDesc(Long userId, Pageable pageable);

    // 根据用户ID和帖子ID查找点赞记录
    Optional<UserLike> findByUserIdAndPostId(Long userId, Long postId);

    // 检查用户是否已点赞某帖子
    boolean existsByUserIdAndPostId(Long userId, Long postId);

    // 根据用户ID和帖子ID删除点赞记录
    @Modifying
    @Query("DELETE FROM UserLike ul WHERE ul.userId = :userId AND ul.postId = :postId")
    void deleteByUserIdAndPostId(@Param("userId") Long userId, @Param("postId") Long postId);

    // 统计用户的点赞数量
    Long countByUserId(Long userId);

    // 统计帖子的点赞数量
    Long countByPostId(Long postId);

    // 根据用户ID删除所有点赞记录
    @Modifying
    @Query("DELETE FROM UserLike ul WHERE ul.userId = :userId")
    void deleteByUserId(@Param("userId") Long userId);
}