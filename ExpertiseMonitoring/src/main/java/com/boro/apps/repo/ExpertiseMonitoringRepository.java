package com.boro.apps.repo;

import com.boro.apps.domain.ExpertiseMonitoring;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ExpertiseMonitoringRepository extends JpaRepository<ExpertiseMonitoring, Long> {

    List<ExpertiseMonitoring> findAll();
    List<ExpertiseMonitoring> findByClientId (String clienId);

    @Override
    void deleteById(Long id);
}

