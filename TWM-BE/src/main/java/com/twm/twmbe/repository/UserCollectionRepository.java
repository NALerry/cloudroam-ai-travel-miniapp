// UserCollectionRepository.java
package com.twm.twmbe.repository;

import com.twm.twmbe.entity.UserCollection;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface UserCollectionRepository extends JpaRepository<UserCollection, Long> {
    Page<UserCollection> findByUserIdOrderByCreatedAtDesc(Long userId, Pageable pageable);
    boolean existsByUserIdAndPostId(Long userId, Long postId);
    void deleteByUserIdAndPostId(Long userId, Long postId);
    Long countByUserId(Long userId);

    @Modifying
    @Query("DELETE FROM UserCollection uc WHERE uc.userId = :userId")
    void deleteByUserId(@Param("userId") Long userId);
}