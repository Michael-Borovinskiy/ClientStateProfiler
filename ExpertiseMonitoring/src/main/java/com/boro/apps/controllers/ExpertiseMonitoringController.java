package com.boro.apps.controllers;


import com.boro.apps.domain.ExpertiseMonitoring;
import com.boro.apps.domain.ExpertiseMonitoringDto;
import com.boro.apps.service.ExpertiseMonitoringServiceImpl;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequiredArgsConstructor
@RequestMapping("/finmonitoring/v1")
public class ExpertiseMonitoringController {

    private final ExpertiseMonitoringServiceImpl expertiseMonitoringService;
    private static final Logger log = LoggerFactory.getLogger(ExpertiseMonitoringController.class);

    @GetMapping("/expertises")
    public String getAllExpertisesMonitoring(Model model) {
        model.addAttribute("expertisesAll", expertiseMonitoringService.getAll());
        return "found_res";
    }

    @GetMapping("/expertises/expertise")
    public String getExpertiseMonitoringByIdClientId(@RequestParam(name = "id", required = false) Long id,
                                                     @RequestParam(name = "clientId", required = false) String clientId, Model model) {

        log.info("getExpertiseMonitoringByIdClientId with id: " + id + " and clientId: " + clientId);
        if (id != null && clientId == null) {
            model.addAttribute("expertiseById", expertiseMonitoringService.getExpertiseMonitoring(id).orElseGet(new ExpertiseMonitoring()::toDto));
            return "upd_res";
        } else {
            model.addAttribute("expertisesByClientId", expertiseMonitoringService.getExpertiseMonitoringByClientId(clientId));
            return "found_res";
        }
    }

    @PostMapping("/expertises")
    public String saveExpertiseMonitoring(@ModelAttribute("savedExpertise") ExpertiseMonitoringDto expertiseMonitoring, Model model) {
        var expertise = expertiseMonitoringService.addExpertise(expertiseMonitoring);

        model.addAttribute("expertisesByClientId", expertiseMonitoringService.getExpertiseMonitoringByClientId(expertise.clientId()));
        return "found_res";
    }

    @PostMapping("/expertises/expertise")
    public String editExpertiseMonitoring(@RequestParam(name = "id", required = false) Long id, @ModelAttribute("editedExpertise") ExpertiseMonitoringDto expertiseMonitoring, Model model) {
        var expertise = expertiseMonitoringService.editExpertiseMonitoring(expertiseMonitoring, id);

        model.addAttribute("expertisesByClientId", expertiseMonitoringService.getExpertiseMonitoringByClientId(expertise.clientId()));
        return "found_res";
    }

    @DeleteMapping("/expertises/expertise/{id}")
    public String deleteExpertiseMonitoring(@PathVariable("id") Long id) {
        expertiseMonitoringService.removeExpertiseMonitoringById(id);
        return "expertises";
    }

    @GetMapping("/save_res")
    public String save_res() {
        return "save_res";
    }

    @GetMapping("/upd_res")
    public String upd_res() {
        return "upd_res";
    }

    @GetMapping("/index")
    public String index() {
        return "index";
    }

    @GetMapping("/expertises_main")
    public String expertises_main() {
        return "expertises_main";
    }

}