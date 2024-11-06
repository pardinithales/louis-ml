<script type="text/javascript">
		$(document).ready(function() {
		    $('.select2').select2({
				selectOnClose: false,
				"language": {
			       // "noResults": function(){
			       //     	return 'Não há resultados';
			       // }
			   },
			    escapeMarkup: function (markup) {
			        return markup;
			    }
			});
		});

		function showToastNotification(type, message) {

			var toast = document.getElementById('toastNotification');
			var toastBody = toast.querySelector('.toast-body');
			var toastHeader = toast.querySelector('.toast-header');
			var toastCloseButton = toast.querySelector('.btn-close');

			toast.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info');
			toast.classList.add('bg-' + type);

			toastBody.innerHTML = message;

			toast.classList.remove('d-none');
			var bootstrapToast = new bootstrap.Toast(toast);
			bootstrapToast.show();

			setTimeout(function() {
				bootstrapToast.hide();
				toastBody.innerHTML = '';
				toastHeader.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info');
			}, 3000);

		}
	</script>

</footer><script src="https://kit.fontawesome.com/1935e00f36.js" crossorigin="anonymous"></script>

<script type="text/javascript">
	var flagLimpaSelect = false;

	function limparSelects() {

		flagLimpaSelect = true;
		var selects = document.querySelectorAll('select');

		selects.forEach(function(select) {
			$(select).val('-').trigger('change');
		});

		document.getElementById('brain').style.display = 'none';
		document.getElementById('responses').style.display = 'none';
		document.getElementById('id-side-symptom1').style.display = 'none';
		document.getElementById('id-side-symptom2').style.display = 'none';
		document.getElementById('id-side-symptom3').style.display = 'none';
		document.getElementById('id-side-symptom4').style.display = 'none';

		setTimeout(function() {
			flagLimpaSelect = false;
		}, 500);

	}

	function validaSide(symptom) {

		if (!flagLimpaSelect) {
			field = symptom.id;
			symptom_val = symptom.value;

			// var obj = JSON.parse('[{"iddata_set":"4458","sign":"Abducens palsy (VI - nucleus)","syndrome":"Foville syndrome","is_ipsilateral":"no"},{"iddata_set":"395","sign":"Abducens palsy (VI)","syndrome":"Brissaud-Sicard Syndrome","is_ipsilateral":"yes"},{"iddata_set":"4559","sign":"Abulia","syndrome":"Anterior cerebral artery","is_ipsilateral":"NA"},{"iddata_set":"377","sign":"Abulia and\/or disinhibition","syndrome":"Bilateral ACA territory syndrome","is_ipsilateral":"NA"},{"iddata_set":"4531","sign":"Acalculia","syndrome":"Middle cerebral artery, posterior division","is_ipsilateral":"no"},{"iddata_set":"2832","sign":"Achromatopsia (inability to perceive color)","syndrome":"Temporal lobe (fusiform or lingual gyri) syndrome","is_ipsilateral":"NA"},{"iddata_set":"4432","sign":"Acute back pain","syndrome":"Anterior spinal artery syndrome (cervical portion)","is_ipsilateral":"NA"},{"iddata_set":"861","sign":"Agraphia","syndrome":"Gerstmann Syndrome","is_ipsilateral":"NA"},{"iddata_set":"865","sign":"Alexia","syndrome":"Gerstmann Syndrome","is_ipsilateral":"NA"},{"iddata_set":"1131","sign":"Alexia Pure (reading difficulty)","syndrome":"Left Temporal lobe (fusiform) AND callosal fibers at the splenium syndrome","is_ipsilateral":"NA"},{"iddata_set":"1127","sign":"Alexia with agraphia","syndrome":"Left Temporal lobe (angular gyrus), extensive syndrome","is_ipsilateral":"NA"},{"iddata_set":"1998","sign":"Altered consciousness","syndrome":"Percheron artery syndrome","is_ipsilateral":"NA"},{"iddata_set":"4627","sign":"Anosognosia","syndrome":"Anton's Syndrome","is_ipsilateral":"NA"},{"iddata_set":"2282","sign":"Anterograde amnesia","syndrome":"Posterior choroidal artery syndrome","is_ipsilateral":"NA"},{"iddata_set":"3096","sign":"Apathy","syndrome":"Thalamus (Ventral Anterior, Ventrolateral and Medial Dorsal Nuclei) syndrome","is_ipsilateral":"NA"},{"iddata_set":"1932","sign":"Aphasia","syndrome":"Partial Anterior Circulation Syndrome","is_ipsilateral":"NA"},{"iddata_set":"1900","sign":"Aphasia (global)","syndrome":"Partial Anterior Circulation Syndrome","is_ipsilateral":"NA"},{"iddata_set":"2002","sign":"Aphasia (impaired comprehension and fluency)","syndrome":"Percheron artery syndrome","is_ipsilateral":"NA"},{"iddata_set":"1980","sign":"Aphasia (impaired comprehension)","syndrome":"Partial Anterior Circulation Syndrome - Inferior Division Syndrome","is_ipsilateral":"NA"},{"iddata_set":"1990","sign":"Aphasia (impaired fluency)","syndrome":"Partial Anterior Circulation Syndrome - Superior Division Syndrome","is_ipsilateral":"NA"},{"iddata_set":"3160","sign":"Apraxia","syndrome":"Thalamus (Ventral Anterior, Ventrolateral and Medial Dorsal Nuclei) syndrome","is_ipsilateral":"NA"},{"iddata_set":"217","sign":"Apraxia of gaze","syndrome":"Balint Syndrome","is_ipsilateral":"NA"},{"iddata_set":"257","sign":"Ataxia","syndrome":"Benedikts syndrome","is_ipsilateral":"no"},{"iddata_set":"4086","sign":"Ataxia (limb bilateral)","syndrome":"Wernekinck comissure syndrome","is_ipsilateral":"no"},{"iddata_set":"365","sign":"Ataxia (limb unilateral)","syndrome":"Benedikts syndrome","is_ipsilateral":"no"},{"iddata_set":"2827","sign":"Ataxia (truncal)","syndrome":"Superior medial cerebellum","is_ipsilateral":"NA"},{"iddata_set":"2018","sign":"Ataxic hemiparesis","syndrome":"Pons (basal paramedian) syndrome","is_ipsilateral":"NA"},{"iddata_set":"2034","sign":"Auditory hallucination","syndrome":"Pons (bilateral) syndrome","is_ipsilateral":"NA"},{"iddata_set":"4438","sign":"Autonomic dysfunction (hypotension, bradycardia, impaired temperature regulation)","syndrome":"Anterior spinal artery syndrome (cervical portion)","is_ipsilateral":"no"},{"iddata_set":"1876","sign":"Bilateral Lid retraction","syndrome":"Parinaud syndrome","is_ipsilateral":"NA"},{"iddata_set":"4436","sign":"Bilateral sensory loss (pain and temperature)","syndrome":"Anterior spinal artery syndrome (cervical portion)","is_ipsilateral":"no"},{"iddata_set":"4511","sign":"Brachiofacial hemiparesis","syndrome":"Middle cerebral artery (M1)","is_ipsilateral":"no"},{"iddata_set":"4525","sign":"Broca aphasia (dominant hemisphere)","syndrome":"Middle cerebral artery, anterior division","is_ipsilateral":"NA"},{"iddata_set":"4629","sign":"Central hypoventilation \/ Apnea","syndrome":"Ondine's Syndrome","is_ipsilateral":"NA"},{"iddata_set":"2020","sign":"Cheiro-oral sensory disturbances","syndrome":"Pons (basal paramedian) syndrome","is_ipsilateral":"no"},{"iddata_set":"269","sign":"Chorea","syndrome":"Benedikts syndrome","is_ipsilateral":"no"},{"iddata_set":"2266","sign":"Cognitive dysfunction","syndrome":"Posterior choroidal artery syndrome","is_ipsilateral":"NA"},{"iddata_set":"881","sign":"Confus\u00e3o direita - esquerda","syndrome":"Gerstmann Syndrome","is_ipsilateral":"NA"},{"iddata_set":"403","sign":"Confusion and\/or Agitation","syndrome":"Caudate nucleus syndrome","is_ipsilateral":"NA"},{"iddata_set":"1828","sign":"Conjugate deviation of the eyes","syndrome":"Parinaud syndrome","is_ipsilateral":"NA"},{"iddata_set":"4556","sign":"Contralateral leg weakness","syndrome":"Anterior cerebral artery","is_ipsilateral":"no"},{"iddata_set":"1840","sign":"Convergence impaired","syndrome":"Parinaud syndrome","is_ipsilateral":"NA"},{"iddata_set":"2110","sign":"Corneal hyperesthesia","syndrome":"Pons (dorsolateral \/ Lower) syndrome","is_ipsilateral":"yes"},{"iddata_set":"222","sign":"Cortical blindness","syndrome":"Balint Syndrome","is_ipsilateral":"NA"},{"iddata_set":"457","sign":"Cortical sensory loss","syndrome":"Deep middle cerebral artery syndrome","is_ipsilateral":"NA"},{"iddata_set":"4477","sign":"Deafness","syndrome":"Anterior inferior cerebellar artery (AICA) syndrome","is_ipsilateral":"yes"},{"iddata_set":"1168","sign":"Diplopia","syndrome":"Medial Medullary Infarction (Dejerine)","is_ipsilateral":"NA"},{"iddata_set":"2010","sign":"Disorientation","syndrome":"Percheron artery syndrome","is_ipsilateral":"NA"},{"iddata_set":"353","sign":"Dysarthria","syndrome":"Benedikts syndrome","is_ipsilateral":"NA"},{"iddata_set":"1264","sign":"Dysarthria-ataxia","syndrome":"Midbrain (anterolateral) syndrome","is_ipsilateral":"NA"},{"iddata_set":"2113","sign":"Dysartrhria","syndrome":"Pons (dorsolateral \/ Lower) syndrome","is_ipsilateral":"yes"},{"iddata_set":"877","sign":"Dyscalculia","syndrome":"Gerstmann Syndrome","is_ipsilateral":"NA"},{"iddata_set":"4098","sign":"Dysdiadochokinesis (bilateral)","syndrome":"Wernekinck comissure syndrome","is_ipsilateral":"no"},{"iddata_set":"851","sign":"Dysfagia","syndrome":"Foix-Chavany-Marie","is_ipsilateral":"NA"},{"iddata_set":"400","sign":"Dysmetria","syndrome":"Caudal cerebellum syndrome","is_ipsilateral":"yes"},{"iddata_set":"785","sign":"Dysphagia","syndrome":"Dysarthria-clumsy hand (lacunar)","is_ipsilateral":"NA"},{"iddata_set":"4182","sign":"Dysphonia","syndrome":"Tapia syndrome","is_ipsilateral":"NA"},{"iddata_set":"329","sign":"Dystonia","syndrome":"Benedikts syndrome","is_ipsilateral":"no"},{"iddata_set":"4077","sign":"Earache","syndrome":"Gell\u00e9 syndrome","is_ipsilateral":"NA"},{"iddata_set":"405","sign":"Emotional Disturbances","syndrome":"Caudate nucleus syndrome","is_ipsilateral":"NA"},{"iddata_set":"3176","sign":"Euphoria","syndrome":"Thalamus (Ventral Anterior, Ventrolateral and Medial Dorsal Nuclei) syndrome","is_ipsilateral":"NA"},{"iddata_set":"849","sign":"Facial and pharyngeal hypotonia","syndrome":"Foix-Chavany-Marie","is_ipsilateral":"NA"},{"iddata_set":"383","sign":"Facial cramps","syndrome":"Brissaud-Sicard Syndrome","is_ipsilateral":"NA"},{"iddata_set":"2111","sign":"Facial pain","syndrome":"Pons (dorsolateral \/ Lower) syndrome","is_ipsilateral":"yes"},{"iddata_set":"57","sign":"Facial palsy","syndrome":"Anterior Choroidal Artery Syndrome","is_ipsilateral":"NA"},{"iddata_set":"33","sign":"Facial palsy (bilateral)","syndrome":"Anterior Choroidal Artery Syndrome","is_ipsilateral":"NA"},{"iddata_set":"4454","sign":"Facial palsy (CN VII - nucleus)","syndrome":"Foville syndrome","is_ipsilateral":"NA"},{"iddata_set":"4475","sign":"Facial palsy (lower motor neuron)","syndrome":"Anterior inferior cerebellar artery (AICA) syndrome","is_ipsilateral":"no"},{"iddata_set":"869","sign":"Finger agnosia","syndrome":"Gerstmann Syndrome","is_ipsilateral":"NA"},{"iddata_set":"1126","sign":"Gait ataxia","syndrome":"Lateral inferior cerebellum syndrome","is_ipsilateral":"NA"},{"iddata_set":"902","sign":"Gait instability","syndrome":"Lateral Medullary Infarction (Wallenberg)","is_ipsilateral":"NA"},{"iddata_set":"4515","sign":"Gaze deviation","syndrome":"Middle cerebral artery (M1)","is_ipsilateral":"no"},{"iddata_set":"4535","sign":"Gerstmann's syndrome","syndrome":"Middle cerebral artery, posterior division","is_ipsilateral":"no"},{"iddata_set":"910","sign":"Headache","syndrome":"Lateral Medullary Infarction (Wallenberg)","is_ipsilateral":"NA"},{"iddata_set":"1159","sign":"Hearing loss","syndrome":"Marie-Foix syndrome","is_ipsilateral":"NA"},{"iddata_set":"4479","sign":"Hemiataxia","syndrome":"Anterior inferior cerebellar artery (AICA) syndrome","is_ipsilateral":"no"},{"iddata_set":"1982","sign":"Hemineglect","syndrome":"Partial Anterior Circulation Syndrome - Inferior Division Syndrome","is_ipsilateral":"no"},{"iddata_set":"41","sign":"Hemiparesis \/ Hemiplegia","syndrome":"Anterior Choroidal Artery Syndrome","is_ipsilateral":"NA"},{"iddata_set":"1204","sign":"Hemiparesis \/ Hemiplegia (except face)","syndrome":"Medial Medullary Infarction (Dejerine)","is_ipsilateral":"no"},{"iddata_set":"918","sign":"Hiccups","syndrome":"Lateral Medullary Infarction (Wallenberg)","is_ipsilateral":"NA"},{"iddata_set":"926","sign":"Hoarseness","syndrome":"Lateral Medullary Infarction (Wallenberg)","is_ipsilateral":"NA"},{"iddata_set":"293","sign":"Holmes tremor","syndrome":"Benedikts syndrome","is_ipsilateral":"no"},{"iddata_set":"4110","sign":"Holmes tremor (bilateral)","syndrome":"Wernekinck comissure syndrome","is_ipsilateral":"no"},{"iddata_set":"9","sign":"Homonymous hemianopia","syndrome":"Anterior Choroidal Artery Syndrome","is_ipsilateral":"NA"},{"iddata_set":"4471","sign":"Horizontal gaze impairment","syndrome":"Locked-in Syndrome","is_ipsilateral":"no"},{"iddata_set":"391","sign":"Horizontal gaze palsy","syndrome":"Brissaud-Sicard Syndrome","is_ipsilateral":"yes"},{"iddata_set":"2298","sign":"Horizontal Sectoranopia","syndrome":"Posterior choroidal artery syndrome","is_ipsilateral":"no"},{"iddata_set":"934","sign":"Horner syndrome","syndrome":"Lateral Medullary Infarction (Wallenberg)","is_ipsilateral":"yes"},{"iddata_set":"1156","sign":"Hyperalgesia","syndrome":"Marie-Foix syndrome","is_ipsilateral":"no"},{"iddata_set":"3208","sign":"Hypophonia","syndrome":"Thalamus (Ventral Anterior, Ventrolateral and Medial Dorsal Nuclei) syndrome","is_ipsilateral":"NA"},{"iddata_set":"1362","sign":"Internuclear ophthalmoplegia (INO)","syndrome":"Midbrain (anteromedial) syndrome","is_ipsilateral":"NA"},{"iddata_set":"305","sign":"Large pupils (mydriasis)","syndrome":"Benedikts syndrome","is_ipsilateral":"no"},{"iddata_set":"401","sign":"Lateropulsion","syndrome":"Caudal cerebellum syndrome","is_ipsilateral":"yes"},{"iddata_set":"4557","sign":"Leg sensory loss","syndrome":"Anterior cerebral artery","is_ipsilateral":"no"},{"iddata_set":"4582","sign":"Limb weakness (contralateral or bilateral)","syndrome":"Basilar perforators","is_ipsilateral":"no"},{"iddata_set":"2070","sign":"Locked-in","syndrome":"Pons (bilateral) syndrome","is_ipsilateral":"NA"},{"iddata_set":"2900","sign":"Loss of taste sensation","syndrome":"Thalamic syndrome (Dejerine and Roussy Syndrome)","is_ipsilateral":"no"},{"iddata_set":"1422","sign":"Macropsia (objects appear larger)","syndrome":"Occipital lobe syndrome","is_ipsilateral":"NA"},{"iddata_set":"4069","sign":"Mastication muscles paralysis","syndrome":"Grenet syndrome","is_ipsilateral":"no"},{"iddata_set":"2014","sign":"Memory loss","syndrome":"Percheron artery syndrome","is_ipsilateral":"NA"},{"iddata_set":"1426","sign":"Metamorphopsia (distorted in size)","syndrome":"Occipital lobe syndrome","is_ipsilateral":"NA"},{"iddata_set":"1430","sign":"Micropsia (objects appear smaller)","syndrome":"Occipital lobe syndrome","is_ipsilateral":"NA"},{"iddata_set":"49","sign":"Monoparesis (inferior limb)","syndrome":"Anterior Choroidal Artery Syndrome","is_ipsilateral":"NA"},{"iddata_set":"25","sign":"Muteness","syndrome":"Anterior Choroidal Artery Syndrome","is_ipsilateral":"NA"},{"iddata_set":"950","sign":"Nausea\/vomiting","syndrome":"Lateral Medullary Infarction (Wallenberg)","is_ipsilateral":"NA"},{"iddata_set":"1852","sign":"Nystagmus (convergence-retraction)","syndrome":"Parinaud syndrome","is_ipsilateral":"NA"},{"iddata_set":"966","sign":"Nystagmus (horizontal-rotational)","syndrome":"Lateral Medullary Infarction (Wallenberg)","is_ipsilateral":"yes"},{"iddata_set":"958","sign":"Nystagmus (horizontal)","syndrome":"Lateral Medullary Infarction (Wallenberg)","is_ipsilateral":"yes"},{"iddata_set":"1216","sign":"Nystagmus (upbeat)","syndrome":"Medial Medullary Infarction (Dejerine)","is_ipsilateral":"NA"},{"iddata_set":"2074","sign":"Ocular bobbing","syndrome":"Pons (bilateral) syndrome","is_ipsilateral":"NA"},{"iddata_set":"281","sign":"Oculomotor palsy (III)","syndrome":"Benedikts syndrome","is_ipsilateral":"yes"},{"iddata_set":"4041","sign":"Oculopalatal tremor","syndrome":"Oculopalatal myoclonus","is_ipsilateral":"no"},{"iddata_set":"2078","sign":"One-and-a-half syndrome","syndrome":"Pons (bilateral) syndrome","is_ipsilateral":"NA"},{"iddata_set":"252","sign":"opic ataxia","syndrome":"Balint Syndrome","is_ipsilateral":"NA"},{"iddata_set":"1151","sign":"Optic aphasia","syndrome":"Left temporooccipital lobe (frequent extension to callosal interhemispheric fibers) syndrome","is_ipsilateral":"NA"},{"iddata_set":"227","sign":"Optic ataxia","syndrome":"Balint Syndrome","is_ipsilateral":"NA"},{"iddata_set":"2202","sign":"Optokinetic response impaired","syndrome":"Posterior choroidal artery syndrome","is_ipsilateral":"no"},{"iddata_set":"2916","sign":"Pain in extremities","syndrome":"Thalamic syndrome (Dejerine and Roussy Syndrome)","is_ipsilateral":"no"},{"iddata_set":"2082","sign":"Palatal myoclonus","syndrome":"Pons (bilateral) syndrome","is_ipsilateral":"NA"},{"iddata_set":"4262","sign":"Palatal palsy","syndrome":"Schmidt syndrome","is_ipsilateral":"no"},{"iddata_set":"379","sign":"Paraparesis","syndrome":"Bilateral ACA territory syndrome","is_ipsilateral":"NA"},{"iddata_set":"3240","sign":"Paraphasia","syndrome":"Thalamus (Ventral Anterior, Ventrolateral and Medial Dorsal Nuclei) syndrome","is_ipsilateral":"NA"},{"iddata_set":"1222","sign":"Paresthesia","syndrome":"Medial Medullary Infarction (Dejerine)","is_ipsilateral":"NA"},{"iddata_set":"317","sign":"Parkinsonism","syndrome":"Benedikts syndrome","is_ipsilateral":"no"},{"iddata_set":"232","sign":"Peripheral visual inattention","syndrome":"Balint Syndrome","is_ipsilateral":"NA"},{"iddata_set":"3256","sign":"Perseveration","syndrome":"Thalamus (Ventral Anterior, Ventrolateral and Medial Dorsal Nuclei) syndrome","is_ipsilateral":"NA"},{"iddata_set":"2086","sign":"Pinpoint pupils","syndrome":"Pons (bilateral) syndrome","is_ipsilateral":"NA"},{"iddata_set":"1434","sign":"Polyopia (multiple images)","syndrome":"Occipital lobe syndrome","is_ipsilateral":"NA"},{"iddata_set":"4473","sign":"Preservation of cortical funcion","syndrome":"Locked-in Syndrome","is_ipsilateral":"no"},{"iddata_set":"4472","sign":"Preservation of vertical gaze","syndrome":"Locked-in Syndrome","is_ipsilateral":"no"},{"iddata_set":"381","sign":"Prosopagnosia (inability to recognize previously familiar faces)","syndrome":"Bilateral Temporal lobe (fusiform gyrus) syndrome","is_ipsilateral":"NA"},{"iddata_set":"974","sign":"Ptosis","syndrome":"Lateral Medullary Infarction (Wallenberg)","is_ipsilateral":"NA"},{"iddata_set":"1864","sign":"Pupillary light-near dissociation","syndrome":"Parinaud syndrome","is_ipsilateral":"NA"},{"iddata_set":"1984","sign":"Quadrantanopia","syndrome":"Partial Anterior Circulation Syndrome - Inferior Division Syndrome","is_ipsilateral":"no"},{"iddata_set":"1993","sign":"Quadrantanopia (inferior)","syndrome":"Partial Anterior Circulation Syndrome - Superior Division Syndrome","is_ipsilateral":"NA"},{"iddata_set":"2834","sign":"Quadrantanopia (superior)","syndrome":"Temporal lobe (lower bank of the striate cortex) syndrome","is_ipsilateral":"NA"},{"iddata_set":"2094","sign":"Quadriparesis","syndrome":"Pons (bilateral) syndrome","is_ipsilateral":"NA"},{"iddata_set":"65","sign":"Quadruple Sectoranopia","syndrome":"Anterior Choroidal Artery Syndrome","is_ipsilateral":"no"},{"iddata_set":"4440","sign":"Respiratory failure","syndrome":"Anterior spinal artery syndrome (cervical portion)","is_ipsilateral":"no"},{"iddata_set":"873","sign":"Right-left confusion","syndrome":"Gerstmann Syndrome","is_ipsilateral":"NA"},{"iddata_set":"237","sign":"Saccades impairment (except vestibular quick phases)","syndrome":"Balint Syndrome","is_ipsilateral":"NA"},{"iddata_set":"2234","sign":"Sectoranopia","syndrome":"Posterior choroidal artery syndrome","is_ipsilateral":"no"},{"iddata_set":"17","sign":"Sensory loss","syndrome":"Anterior Choroidal Artery Syndrome","is_ipsilateral":"NA"},{"iddata_set":"1228","sign":"Sensory loss (deep)","syndrome":"Medial Medullary Infarction (Dejerine)","is_ipsilateral":"no"},{"iddata_set":"1598","sign":"Sensory loss (except face)","syndrome":"Opalsky syndrome (only if hemiparesia or hemiplegia are present)","is_ipsilateral":"no"},{"iddata_set":"1610","sign":"Sensory loss (face)","syndrome":"Opalsky syndrome (only if hemiparesia or hemiplegia are present)","is_ipsilateral":"yes"},{"iddata_set":"4242","sign":"Sensory loss (pain and temperature; except face)","syndrome":"Spiller syndrome","is_ipsilateral":"NA"},{"iddata_set":"4288","sign":"Sensory loss (pain and temperature; face)","syndrome":"Hemimedullary syndrome (Reinhold syndrome)","is_ipsilateral":"no"},{"iddata_set":"1157","sign":"Sensory loss (pain and temperature)","syndrome":"Marie-Foix syndrome","is_ipsilateral":"NA"},{"iddata_set":"4234","sign":"Sensory loss (proprioception and vibration)","syndrome":"Spiller syndrome","is_ipsilateral":"no"},{"iddata_set":"242","sign":"Simultanagnosia","syndrome":"Balint Syndrome","is_ipsilateral":"NA"},{"iddata_set":"1888","sign":"Skew deviation","syndrome":"Parinaud syndrome","is_ipsilateral":"NA"},{"iddata_set":"247","sign":"Smooth pursuit deficits","syndrome":"Balint Syndrome","is_ipsilateral":"NA"},{"iddata_set":"2830","sign":"Sphinecter dysfunction","syndrome":"Superolateral and medial superior frontal gyrus syndrome","is_ipsilateral":"NA"},{"iddata_set":"4568","sign":"Thalamic aphasia","syndrome":"Posterior cerebral artery (PCA) - precommunicating part","is_ipsilateral":"no"},{"iddata_set":"2098","sign":"Tinnitus","syndrome":"Pons (bilateral) syndrome","is_ipsilateral":"NA"},{"iddata_set":"801","sign":"Tongue paralysis","syndrome":"Dysarthria-clumsy hand (lacunar)","is_ipsilateral":"no"},{"iddata_set":"2794","sign":"Topographagnosia (Topographic Disorientation)","syndrome":"Posterior cingulate syndrome","is_ipsilateral":"NA"},{"iddata_set":"4470","sign":"Total immobility (all voluntary muscles)","syndrome":"Locked-in Syndrome","is_ipsilateral":"no"},{"iddata_set":"4128","sign":"Trapezius and sternocleidomastoid palsy","syndrome":"Tapia syndrome","is_ipsilateral":"no"},{"iddata_set":"2824","sign":"Tremor","syndrome":"Superior cerebellum and pons syndrome","is_ipsilateral":"yes"},{"iddata_set":"1","sign":"Uncontrollable crying and laughing","syndrome":"Anterior Choroidal Artery Syndrome","is_ipsilateral":"NA"},{"iddata_set":"402","sign":"Vertigo","syndrome":"Caudal cerebellum syndrome","is_ipsilateral":"NA"},{"iddata_set":"1145","sign":"VIsual agnosia","syndrome":"Left Temporal lobe (more anterior segments of fusiform gyri) syndrome","is_ipsilateral":"NA"},{"iddata_set":"2840","sign":"Visual agnosia (apperceptive)","syndrome":"Temporal lobe (more posterior segments of lingual and fusiform gyri) syndrome","is_ipsilateral":"NA"},{"iddata_set":"1139","sign":"Visual agnosia (associative)","syndrome":"Left Temporal lobe (more anterior segments of fusiform gyri) syndrome","is_ipsilateral":"NA"},{"iddata_set":"4628","sign":"Visual Confabulation","syndrome":"Anton's Syndrome","is_ipsilateral":"NA"},{"iddata_set":"4514","sign":"Visual field defect","syndrome":"Middle cerebral artery (M1)","is_ipsilateral":"no"},{"iddata_set":"1438","sign":"Visual hallucination","syndrome":"Occipital lobe syndrome","is_ipsilateral":"yes"},{"iddata_set":"998","sign":"Vocal chord paralysis","syndrome":"Lateral Medullary Infarction (Wallenberg)","is_ipsilateral":"yes"},{"iddata_set":"4530","sign":"Wernicke's aphasia (dominant hemisphere)","syndrome":"Middle cerebral artery, posterior division","is_ipsilateral":"no"}]');

			urldata = "https://louis-stroke.com/json/symptons"
			$.getJSON(urldata, function(obj) {

				for (var i = 0; i < obj.length; i++) {
					if (obj[i].iddata_set == symptom_val) {
						if (obj[i].is_ipsilateral == 'NA') {
							document.getElementById('id-side-' + field).style.display = 'none';
						} else {
							document.getElementById('id-side-' + field).style.display = 'grid';
						}
					}
				}
			});
		}

	}


	validaContador();

	function validaContador() {

		const inps = document.getElementsByClassName('symptoms');
		var cont = 0;

		Array.from(inps).forEach(element => {
			validaPreenchimento(element);
		});

		function validaPreenchimento(input) {
			if (input.value != '-') {
				cont = cont + 1;
			}
		}

		return cont;

	}

	function validaSintomas() {

		cont = validaContador();

		if (cont >= 1) {

			if (!flagLimpaSelect) {
				var symptom1 = document.getElementById('symptom1').value;
				var symptom1_text = document.getElementById('symptom1').options[document.getElementById('symptom1').selectedIndex].text;
				var sidesymptom1 = document.getElementById('side-symptom1').value;

				var symptom2 = document.getElementById('symptom2').value;
				var symptom2_text = document.getElementById('symptom2').options[document.getElementById('symptom2').selectedIndex].text;
				var sidesymptom2 = document.getElementById('side-symptom2').value;

				var symptom3 = document.getElementById('symptom3').value;
				var symptom3_text = document.getElementById('symptom3').options[document.getElementById('symptom3').selectedIndex].text;
				var sidesymptom3 = document.getElementById('side-symptom3').value;

				var symptom4 = document.getElementById('symptom4').value;
				var symptom4_text = document.getElementById('symptom4').options[document.getElementById('symptom4').selectedIndex].text;
				var sidesymptom4 = document.getElementById('side-symptom4').value;
				
				var symptom5 = '-';
				var sidesymptom5 = '-';		
				

				document.getElementById('brain').style.display = 'block';
				document.getElementById('responses').style.display = 'none';
				document.getElementById('symptom1').disabled = true;
				document.getElementById('side-symptom1').disabled = true;
				document.getElementById('symptom2').disabled = true;
				document.getElementById('side-symptom2').disabled = true;
				document.getElementById('symptom3').disabled = true;
				document.getElementById('side-symptom3').disabled = true;
				document.getElementById('symptom4').disabled = true;
				document.getElementById('side-symptom4').disabled = true;

				$('#image-reference-first-vessel').hide();
				$('#image-reference-second-vessel').hide();
				$('#image-reference-third-vessel').hide();
				$('#image-reference-fourth-vessel').hide();

				clear_spans();

				url = 'https://louis-stroke.com/home/processing/?symptom1=' + symptom1 + '&symptom2=' + symptom2 + '&symptom3=' + symptom3 + '&symptom4=' + symptom4 + '&symptom5=' + symptom5 + '&sidesymptom1=' + sidesymptom1 + '&sidesymptom2=' + sidesymptom2 + '&sidesymptom3=' + sidesymptom3 + '&sidesymptom4=' + sidesymptom4 + '&sidesymptom5=' + sidesymptom5;

				// console.log(url);

				$.getJSON(url, function(data) {

					// console.log(data);

					var baseImageUrl = 'https://louis-stroke.com/assets/images/references/';
					document.getElementById('responses').style.display = 'block';
					document.getElementById('brain').style.display = 'none';
					document.getElementById('payload').value = url;

					if (data[0].symptom) {
						document.getElementById(
							'clinical-syndrome-first').innerHTML = data[0].symptom;
						document.getElementById('lesion-side-first').innerHTML = data[0].lesion_side;

						document.getElementById('probable-syndrome-first').innerHTML = data[0].symptom;

						$('#container-image-reference-first').show();
						$('#container-image-reference-first-vessel').show();

						if (data[0]['reference_image']['vessel'] !== 'NA.png' && (data[0]['reference_image']['vessel'] !== data[0]['reference_image']['image'])) {
							$('#image-reference-first-vessel').show();
							let imageUrl = baseImageUrl + data[0]['reference_image']['vessel'];
							let img = new Image();
							img.src = imageUrl;
							img.onload = function() {
								$('#image-reference-first-vessel').attr('src', imageUrl);
							};
							img.onerror = function() {
								$('#container-image-reference-first-vessel').hide();
							};
						} else {
							$('#container-image-reference-first-vessel').hide();
						}

						if (data[0]['reference_image']['image'] !== 'NA.png') {
							let imageUrl = baseImageUrl + data[0]['reference_image']['image'];
							let img = new Image();
							img.src = imageUrl;
							img.onload = function() {
								$('#image-reference-first').attr('src', imageUrl);
							};
							img.onerror = function() {
								$('#container-image-reference-first').hide();
							};
						}else{
							$('#container-image-reference-first').hide();
						}					

						document.getElementById('brainstem-location').innerHTML = data[0].locais;
						document.getElementById('arteries-involved').innerHTML = data[0].arterias;
						document.getElementById('important-notes').innerHTML = data[0].notes;

						let all_symps = data[0].all_symp;

						var all_symps_first = document.getElementById('sign-or-symptom-first');

						all_symps.forEach(element => {
							var li = document.createElement('li');

							var span = document.createElement('span');
							span.innerHTML = element.sign;
							
							if (element.sign == symptom1_text || element.sign == symptom2_text || element.sign == symptom3_text || element.sign == symptom4_text) {
								span.classList.add('vermelho');								
							}
							li.appendChild(span);

							all_symps_first.appendChild(li);
						});
						// console.log(all_symps);
					}

					if (data[1]) {

						document.getElementById('second-response').style.display = 'flex';
						document.getElementById('clinical-syndrome-second').innerHTML = data[1].symptom;
						document.getElementById('lesion-side-second').innerHTML = data[1].lesion_side;
						document.getElementById('probable-syndrome-second').innerHTML = data[1].symptom;

						$('#container-image-reference-second').show();
						$('#container-image-reference-second-vessel').show();

						if (data[1]['reference_image']['vessel'] !== 'NA.png' && (data[1]['reference_image']['vessel'] !== data[1]['reference_image']['image'])) {
							$('#image-reference-second-vessel').show();

							var imageUrl = baseImageUrl + data[1]['reference_image']['vessel'];
							var img = new Image();
							img.src = imageUrl;
							img.onload = function() {
								$('#image-reference-second-vessel').attr('src', imageUrl);
							};
							img.onerror = function() {
								$('#container-image-reference-second-vessel').hide();
							};

						} else {
							$('#container-image-reference-second-vessel').hide();
						}

						if (data[1]['reference_image']['image'] !== 'NA.png') {
							let imageUrl = baseImageUrl + data[1]['reference_image']['image'];
							let img = new Image();
							img.src = imageUrl;
							img.onload = function() {
								$('#image-reference-second').attr('src', imageUrl);
							};
							img.onerror = function() {
								$('#container-image-reference-second').hide();
							};					
						}else{
							$('#container-image-reference-second').hide();
						}

						let all_symps = data[1].all_symp;

						var all_symps_first = document.getElementById('sign-or-symptom-second');

						all_symps.forEach(element => {
							var li = document.createElement('li');

							var span = document.createElement('span');
							span.innerHTML = element.sign;
							
							if (element.sign == symptom1_text || element.sign == symptom2_text || element.sign == symptom3_text || element.sign == symptom4_text) {
								span.classList.add('vermelho');								
							}
							li.appendChild(span);

							all_symps_first.appendChild(li);
						});

					} else {

						document.getElementById('second-response').style.display = 'none';

					}

					if (data[2]) {

						document.getElementById('third-response').style.display = 'flex';
						document.getElementById('clinical-syndrome-third').innerHTML = data[2].symptom;
						document.getElementById('lesion-side-third').innerHTML = data[2].lesion_side;
						document.getElementById('probable-syndrome-third').innerHTML = data[2].symptom;

						$('#container-image-reference-third').show();
						$('#container-image-reference-third-vessel').show();

						if (data[2]['reference_image']['vessel'] !== 'NA.png' && (data[2]['reference_image']['vessel'] !== data[2]['reference_image']['image'])) {
							$('#image-reference-third-vessel').show();

							let imageUrl = baseImageUrl + data[2]['reference_image']['vessel'];
							let img = new Image();
							img.src = imageUrl;
							img.onload = function() {
								$('#image-reference-third-vessel').attr('src', imageUrl);
							};
							img.onerror = function() {
								$('#container-image-reference-third-vessel').hide();
							};

						} else {
							$('#container-image-reference-third-vessel').hide();
						}

						if (data[2]['reference_image']['image'] !== 'NA.png') {
							let imageUrl = baseImageUrl + data[2]['reference_image']['image'];
							let img = new Image();
							img.src = imageUrl;
							img.onload = function() {
								$('#image-reference-third').attr('src', imageUrl);
							};
							img.onerror = function() {
								$('#container-image-reference-third').hide();
							};					
						}else{
							$('#container-image-reference-third').hide();
						}

						let all_symps = data[2].all_symp;

						var all_symps_first = document.getElementById('sign-or-symptom-third');

						all_symps.forEach(element => {
							var li = document.createElement('li');

							var span = document.createElement('span');
							span.innerHTML = element.sign;
							
							if (element.sign == symptom1_text || element.sign == symptom2_text || element.sign == symptom3_text || element.sign == symptom4_text) {
								span.classList.add('vermelho');								
							}
							li.appendChild(span);

							all_symps_first.appendChild(li);
						});

					} else {

						document.getElementById('third-response').style.display = 'none';

					}

					if (data[3]) {
						document.getElementById('fourth-response').style.display = 'flex';
						document.getElementById('clinical-syndrome-fourth').innerHTML = data[3].symptom;
						document.getElementById('lesion-side-fourth').innerHTML = data[3].lesion_side;
						document.getElementById('probable-syndrome-fourth').innerHTML = data[3].symptom;

						if (data[3]['reference_image']['vessel'] !== 'NA.png' && (data[3]['reference_image']['vessel'] !== data[3]['reference_image']['image'])) {
							$('#image-reference-fourth-vessel').show();

							let imageUrl = baseImageUrl + data[3]['reference_image']['vessel'];
							let img = new Image();
							img.src = imageUrl;
							img.onload = function() {
								$('#image-reference-fourth-vessel').attr('src', imageUrl);
							};
							img.onerror = function() {
								$('#container-image-reference-fourth-vessel').hide();
							};

						} else {
							$('#image-reference-fourth-vessel').hide();
						}

						if (data[3]['reference_image']['image'] !== 'NA.png') {
							let imageUrl = baseImageUrl + data[3]['reference_image']['image'];
							let img = new Image();
							img.src = imageUrl;
							img.onload = function() {
								$('#image-reference-fourth').attr('src', imageUrl);
							};
							img.onerror = function() {
								$('#container-image-reference-fourth').hide();
							};					
						}else{
							$('#container-image-reference-fourth').hide();
						}

						let all_symps = data[3].all_symp;

						var all_symps_first = document.getElementById('sign-or-symptom-fourth');

						all_symps.forEach(element => {
							
							var li = document.createElement('li');

							var span = document.createElement('span');
							span.innerHTML = element.sign;
							
							if (element.sign == symptom1_text || element.sign == symptom2_text || element.sign == symptom3_text || element.sign == symptom4_text) {
								span.classList.add('vermelho');								
							}
							li.appendChild(span);

							all_symps_first.appendChild(li);
						});

					} else {
						document.getElementById('fourth-response').style.display = 'none';
					}

					document.getElementById('symptom1').disabled = false;
					document.getElementById('side-symptom1').disabled = false;
					document.getElementById('symptom2').disabled = false;
					document.getElementById('side-symptom2').disabled = false;
					document.getElementById('symptom3').disabled = false;
					document.getElementById('side-symptom3').disabled = false;
					document.getElementById('symptom4').disabled = false;
					document.getElementById('side-symptom4').disabled = false;

				});
			}

			

		}
	}

	function clear_spans() {

		document.getElementById('clinical-syndrome-first').innerHTML = '';
		document.getElementById('lesion-side-first').innerHTML = '';

		document.getElementById('clinical-syndrome-second').innerHTML = '';
		document.getElementById('lesion-side-second').innerHTML = '';

		document.getElementById('clinical-syndrome-third').innerHTML = '';
		document.getElementById('lesion-side-third').innerHTML = '';

		document.getElementById('clinical-syndrome-fourth').innerHTML = '';
		document.getElementById('lesion-side-fourth').innerHTML = '';

		document.getElementById('brainstem-location').innerHTML = '';
		document.getElementById('arteries-involved').innerHTML = '';
		document.getElementById('important-notes').innerHTML = '';

		document.getElementById('sign-or-symptom-first').innerHTML = '';
		document.getElementById('sign-or-symptom-second').innerHTML = '';
		document.getElementById('sign-or-symptom-third').innerHTML = '';
		document.getElementById('sign-or-symptom-fourth').innerHTML = '';

	}

	$(function() {
		$('.pop').on('click', function() {
			$('.imagepreview').attr('src', $(this).find('img').attr('src'));
			$('#imagemodal').modal('show');
		});
	});

	$(document).ready(function() {
		$("#suggestion-form").submit(function(e) {
			$("#suggestion-send").attr("disabled", true);
			document.getElementById('suggestion-send').innerHTML = '<div class="spinner-border spinner-border-sm text-light" role="status"> </div> Sending';
		});
	});
</script>



</html>