package com.boro.apps.service;


import com.boro.apps.domain.ExpertiseMonitoring;
import com.boro.apps.domain.ExpertiseMonitoringDto;
import com.boro.apps.domain.ExpertiseType;
import com.boro.apps.repo.ExpertiseMonitoringRepository;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;


import java.sql.Timestamp;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@AllArgsConstructor
public class ExpertiseMonitoringServiceImpl implements ExpertiseMonitoringService {

    private final ExpertiseMonitoringRepository expertiseMonitoringRepository;

    @Override
    @Transactional(readOnly = true)
    public Optional<ExpertiseMonitoringDto> getExpertiseMonitoring(Long id) {
        return expertiseMonitoringRepository.findById(id).map(ExpertiseMonitoring::toDto);
    }

    @Override
    @Transactional(readOnly = true)
    public List<ExpertiseMonitoringDto> getExpertiseMonitoringByClientId(String clientId) {
        return expertiseMonitoringRepository.findByClientId(clientId).stream().map(ExpertiseMonitoring::toDto).collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<ExpertiseMonitoringDto> getAll() {
        return expertiseMonitoringRepository.findAll().stream().map(ExpertiseMonitoring::toDto).collect(Collectors.toList());
    }

    @Override
    @Transactional
    public ExpertiseMonitoringDto addExpertise(ExpertiseMonitoringDto expertiseMonitoring) {

        return expertiseMonitoringRepository.save(ExpertiseMonitoring.builder()
                .expertiseType(ExpertiseType.valueOf(expertiseMonitoring.expertiseType()))
                .clientId(expertiseMonitoring.clientId())
                .status(expertiseMonitoring.status())
                .comment(expertiseMonitoring.comment())
                .dtExpertiseStatus(new Timestamp(System.currentTimeMillis()))
                .build()).toDto();
    }

    @Override
    @Transactional
    public ExpertiseMonitoringDto editExpertiseMonitoring(ExpertiseMonitoringDto expertiseMonitoring, Long id) {

        return expertiseMonitoringRepository.findById(id)
                .map(expertise -> {
                    expertise.setExpertiseType(ExpertiseType.valueOf(expertiseMonitoring.expertiseType()));
                    expertise.setClientId(expertiseMonitoring.clientId());
                    expertise.setStatus(expertiseMonitoring.status());
                    expertise.setComment(expertiseMonitoring.comment());
                    expertise.setDtExpertiseStatus(new Timestamp(System.currentTimeMillis()));
                    return expertiseMonitoringRepository.save(expertise).toDto();
                })
                .orElseGet(() ->
                {
                    var expertise = ExpertiseMonitoring.builder()
                            .expertiseType(ExpertiseType.valueOf(expertiseMonitoring.expertiseType()))
                            .clientId(expertiseMonitoring.clientId())
                            .status(expertiseMonitoring.status())
                            .comment(expertiseMonitoring.comment())
                            .dtExpertiseStatus(new Timestamp(System.currentTimeMillis()))
                            .build();

                    return expertiseMonitoringRepository.save(expertise).toDto();
                });
    }

    @Override
    @Transactional
    public void removeExpertiseMonitoringById(Long id) {
        expertiseMonitoringRepository.deleteById(id);
    }


}
