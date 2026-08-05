class ConfidenceService:
    
    def calculate(self,ranked_docs):
        if not ranked_docs:
            return 'Very Low'
        
        top_score=float(ranked_docs[0][1])
                
        if top_score>=7:
            return 'Very High'
        
        elif top_score>=5:
            return 'High' 
        
        elif top_score>=3:
            return 'Medium'  
             
        else:
            return 'Low'
        
confidence_service=ConfidenceService()        