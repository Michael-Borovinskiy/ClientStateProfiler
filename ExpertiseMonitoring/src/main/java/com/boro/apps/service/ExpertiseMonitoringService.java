package com.boro.apps.service;


import com.boro.apps.domain.ExpertiseMonitoringDto;

import java.util.List;
import java.util.Optional;

public interface ExpertiseMonitoringService {

    Optional<ExpertiseMonitoringDto> getExpertiseMonitoring(Long id);
    List<ExpertiseMonitoringDto> getExpertiseMonitoringByClientId(String clientId);

    List<ExpertiseMonitoringDto> getAll();

    ExpertiseMonitoringDto addExpertise(ExpertiseMonitoringDto expertiseMonitoring);
    ExpertiseMonitoringDto editExpertiseMonitoring(ExpertiseMonitoringDto expertiseMonitoring, Long id);
    void removeExpertiseMonitoringById(Long id);

}
