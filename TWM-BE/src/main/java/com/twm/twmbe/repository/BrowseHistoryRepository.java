package com.twm.twmbe.repository;

import com.twm.twmbe.entity.BrowseHistory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface BrowseHistoryRepository extends JpaRepository<BrowseHistory, Long> {

    // 根据用户ID查找浏览记录，按浏览时间倒序
    Page<BrowseHistory> findByUserIdOrderByBrowseTimeDesc(Long userId, Pageable pageable);

    // 根据用户ID和帖子ID查找浏览记录
    BrowseHistory findByUserIdAndPostId(Long userId, Long postId);

    // 统计用户的浏览记录数量
    Long countByUserId(Long userId);

    // 删除用户的某条浏览记录
    @Modifying
    @Query("DELETE FROM BrowseHistory bh WHERE bh.userId = :userId AND bh.postId = :postId")
    void deleteByUserIdAndPostId(@Param("userId") Long userId, @Param("postId") Long postId);

    // 删除用户的所有浏览记录
    @Modifying
    @Query("DELETE FROM BrowseHistory bh WHERE bh.userId = :userId")
    void deleteByUserId(@Param("userId") Long userId);

    // 删除指定时间之前的浏览记录
    @Modifying
    @Query("DELETE FROM BrowseHistory bh WHERE bh.browseTime < :time")
    void deleteByBrowseTimeBefore(@Param("time") LocalDateTime time);
}