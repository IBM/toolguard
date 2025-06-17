import os
import re
from collections import defaultdict

import nltk

nltk.download('punkt')
import json


class ReferenceEval:
	
	def __init__(self,gt_dir: str, generated_dir: str):
		avgs = [0,0,0]
		p_avgs = [0,0,0]

		ntools = 0
		for tool_file in os.listdir(gt_dir):
			if tool_file.endswith(".json") :
				gtool_file = self.pascal_to_snake(tool_file)
				generated_path = os.path.join(generated_dir,gtool_file)
				ground_truth_path = os.path.join(gt_dir, tool_file)

				ground_truth_spans, gt_span2policy, num_gt_policies = self.references_to_sent_spans(ground_truth_path)
				generated_spans, gen_span2policy, num_gen_policies = self.references_to_sent_spans(generated_path)
				# self.print_sorted_strings(ground_truth_spans)
				# print()
				# self.print_sorted_strings(generated_spans)
				true_positives = 0
				if len(ground_truth_spans)==0:
					continue
				ntools += 1

				covered_in_gt_policies = set()
				correctly_identified_policies = set()
				for s in ground_truth_spans:
					if s in generated_spans:
						covered_in_gt_policies.update(gt_span2policy[s])
						correctly_identified_policies.update(gen_span2policy[s])
						true_positives+=1

				precision = true_positives / len(generated_spans) if generated_spans else 0.0
				recall = true_positives / len(ground_truth_spans) if ground_truth_spans else 0.0
				f1 = (
					2 * precision * recall / (precision + recall)
					if (precision + recall) > 0
					else 0.0
				)

				avgs[0]+=precision
				avgs[1]+=recall
				avgs[2]+=f1

				p_precision = len(correctly_identified_policies)/num_gen_policies if num_gen_policies>0 else 0.0
				p_recall = len(covered_in_gt_policies)/num_gt_policies if num_gt_policies>0 else 0.0
				p_f1 = (
					2 * p_precision * p_recall / (p_precision + p_recall)
					if (p_precision + p_recall) > 0
					else 0.0
				)

				p_avgs[0]+=p_precision
				p_avgs[1]+=p_recall
				p_avgs[2]+=p_f1

				print(f"Tool: {tool_file} Precision: {precision:.2f}, Recall: {recall:.2f}, F1: {f1:.2f} *** "
					  f"policy-level results: Precision: {p_precision:.2f}, Recall: {p_recall:.2f}, F1: {p_f1:.2f}")
				
		print(f"Avg Precision: { avgs[0]/ntools:.2f} Avg Recall: { avgs[1]/ntools:.2f} Avg F1: { avgs[2]/ntools:.2f} *** "
			  f"policy-level stats: Avg Precision: {p_avgs[0]/ntools:.2f} Avg Recall: {p_avgs[1]/ntools:.2f} "
			  f"Avg F1: {p_avgs[2]/ntools:.2f}")
	
	def pascal_to_snake(self,name):
		# Insert underscore before capital letters and convert to lowercase
		s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
		s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
		return s2.lower()
	
	def snake_to_pascal(self,s):
		return ''.join(word.capitalize() for word in s.split('_'))
	
	def clean_field_name(self,field):
		# Remove trailing underscores and convert to PascalCase
		field = field.rstrip('_')
		return self.snake_to_pascal(field)
	
	def print_sorted_strings(self,strings):
		sorted_strings = sorted(strings)
		for s in sorted_strings:
			print(s)
			
	def references_to_sent_spans(self, filepath: str):
		from nltk.tokenize import sent_tokenize
		sentences = []
		references = []
		if not os.path.isfile(filepath):
			print('file does not exist: '+filepath)
			return list(), dict(), 0

		ref2policy = defaultdict(set)
		with open(filepath, 'r') as file:
			policies = json.load(file)
			for p_id, p in enumerate(policies["policies"]):
				p_references = [r.lower().replace("<p>", "").replace("</p>","") for r in p["references"]]
				references.extend(p_references)
				for r in p_references:
					ref2policy[r].add(p_id)

			total_policies = len(policies["policies"])

		sent2policy = defaultdict(set)
		for r, p_ids in ref2policy.items():  #references:
			r_sentences = sent_tokenize(r)
			sentences.extend(r_sentences)
			for s in r_sentences:
				sent2policy[s].update(p_ids)
		tset = set(sentences)

		return list(tset), sent2policy, total_policies
		

if __name__ == '__main__':
	
	# gtdir = '/Users/naamazwerdling/Documents/OASB/policy_validation/airline/GroundTruth'
	# #gendir = '/Users/naamazwerdling/Documents/OASB/policy_validation/airline/final'
	# gendir = '/Users/naamazwerdling/Documents/OASB/policy_validation/airline/final copy 4'
	# #gendir = '/Users/naamazwerdling/Documents/OASB/policy_validation/airline/final with salesforce'
	# #gendir = '/Users/naamazwerdling/Documents/OASB/policy_validation/airline/final_non-existing-tools-rev'
	# #gendir = '/Users/naamazwerdling/Documents/OASB/policy_validation/airline/final copy 5'
	# #gendir = '/Users/naamazwerdling/Documents/OASB/policy_validation/airline/final oas'
	# gendir = '/Users/naamazwerdling/Documents/OASB/policy_validation/airline/final my json'

	gtdir = os.path.join('GT', 'airlines')

	#gendir = os.path.join('output', 'llama-3-3-70b-instruct', 'Step1')
	gendir = os.path.join('output', 'gpt-4o-2024-08-06', 'Step1')
	gendir = '/Users/naamazwerdling/Documents/OASB/policy_validation/airline/outdir2/wiki_sf_rev'
	gendir = '/Users/naamazwerdling/Documents/OASB/policy_validation/airline/outdir2/wiki_full_gpt4'
	gendir = "/Users/naamazwerdling/Documents/OASB/policy_validation/airline/outdir2/full_wiki_gpt4_second"
	gendir = "/Users/naamazwerdling/Documents/OASB/policy_validation/airline/outdir2/full_wiki_gpt4_short_oas3"
	#gendir = os.path.join('output', 'llama-3-3-70b-instruct', 'Step1')
	#gendir = os.path.join('output', 'gpt-4o-mini-2024-07-18', 'Step1')
	#gendir = os.path.join('output', 'gpt-4o-2024-08-06', 'Step1')


	ReferenceEval(gtdir, gendir)
