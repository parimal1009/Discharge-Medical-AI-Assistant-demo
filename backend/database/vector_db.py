"""
Vector Database Management for RAG
Handles PDF processing, embeddings, and semantic search
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List, Dict, Any, Optional
import PyPDF2
from backend.config import settings
from backend.utils.logger import system_logger

class VectorDatabase:
    """Manages vector embeddings and semantic search"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer(settings.EMBEDDINGS_MODEL)
        self.client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"description": "Nephrology knowledge base for RAG"}
        )
        
        system_logger.log_system_event(
            "vector_db_initialized",
            {
                "collection": settings.CHROMA_COLLECTION_NAME,
                "embedding_model": settings.EMBEDDINGS_MODEL
            }
        )
    
    def process_pdf(self, pdf_path: Optional[str] = None) -> List[str]:
        """Extract and chunk text from PDF"""
        pdf_path = pdf_path or settings.PDF_PATH
        
        try:
            pdf_file = Path(pdf_path)
            
            if not pdf_file.exists():
                system_logger.log_error(
                    "vector_db",
                    f"PDF file not found: {pdf_path}"
                )
                return self._get_fallback_knowledge()
            
            # Extract text from PDF
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text += page.extract_text() + "\n"
                    except Exception as e:
                        system_logger.log_error(
                            "vector_db",
                            f"Error extracting page {page_num}: {e}"
                        )
            
            # Chunk the text
            chunks = self._chunk_text(text)
            
            system_logger.log_system_event(
                "pdf_processed",
                {
                    "pdf_path": pdf_path,
                    "num_pages": len(pdf_reader.pages),
                    "num_chunks": len(chunks)
                }
            )
            
            return chunks
            
        except Exception as e:
            system_logger.log_error(
                "vector_db",
                f"Error processing PDF: {e}"
            )
            return self._get_fallback_knowledge()
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        chunk_size = settings.CHUNK_SIZE
        chunk_overlap = settings.CHUNK_OVERLAP
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundaries
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > chunk_size // 2:
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            start = end - chunk_overlap
        
        return chunks
    
    def _get_fallback_knowledge(self) -> List[str]:
        """Return fallback nephrology knowledge if PDF not available"""
        return [
            "Chronic Kidney Disease (CKD) is defined as abnormalities of kidney structure or function, present for greater than 3 months, with implications for health. The staging system is based on GFR (Glomerular Filtration Rate) and albuminuria levels. CKD Stage 1 has normal or high GFR (≥90 mL/min/1.73m²) with kidney damage, Stage 2 has mild reduction (60-89), Stage 3a moderate reduction (45-59), Stage 3b moderate to severe (30-44), Stage 4 severe reduction (15-29), and Stage 5 kidney failure (<15).",
            
            "Management of CKD includes blood pressure control with target <130/80 mmHg, proteinuria reduction using ACE inhibitors or ARBs, glycemic control in diabetics with HbA1c target <7%, dietary modifications including sodium restriction, management of complications like anemia, bone mineral disease, and metabolic acidosis, and preparation for renal replacement therapy.",
            
            "Angiotensin-converting enzyme inhibitors (ACEi) and angiotensin receptor blockers (ARBs) are cornerstone therapies in proteinuric kidney disease. They reduce intraglomerular pressure and proteinuria, slowing CKD progression. Common ACEi include lisinopril, enalapril, and ramipril. Common ARBs include losartan, valsartan, and irbesartan. Monitoring includes serum creatinine (acceptable rise <30% from baseline), potassium levels, and blood pressure.",
            
            "Dietary management in CKD varies by stage. Early stages focus on sodium restriction (<2g/day), adequate but not excessive protein intake. Advanced stages (4-5) require protein restriction (0.6-0.8 g/kg/day), potassium restriction if hyperkalemic, phosphorus restriction (800-1000 mg/day), and fluid management based on urine output and edema status.",
            
            "Acute Kidney Injury (AKI) is defined by KDIGO criteria: increase in serum creatinine by ≥0.3 mg/dL within 48 hours, or increase to ≥1.5 times baseline within 7 days, or urine output <0.5 mL/kg/h for 6 hours. Staging includes Stage 1 (Cr 1.5-1.9x baseline), Stage 2 (Cr 2.0-2.9x baseline), and Stage 3 (Cr ≥3x baseline or Cr ≥4.0 mg/dL or initiation of RRT).",
            
            "Common causes of AKI include prerenal (volume depletion, heart failure, hepatorenal syndrome), intrinsic renal (acute tubular necrosis, acute interstitial nephritis, glomerulonephritis), and postrenal (obstruction). Management focuses on identifying and treating the underlying cause, optimizing hemodynamics, avoiding nephrotoxins, and adjusting medication doses.",
            
            "Diabetic nephropathy is the leading cause of ESRD worldwide. It progresses through stages: stage 1 hyperfiltration with elevated GFR, stage 2 silent stage with thickening of glomerular basement membrane, stage 3 microalbuminuria (30-300 mg/day), stage 4 overt nephropathy with macroalbuminuria (>300 mg/day), and stage 5 ESRD. Prevention and management include strict glycemic control, blood pressure control, ACEi/ARB therapy, and SGLT2 inhibitors.",
            
            "SGLT2 inhibitors (empagliflozin, dapagliflozin, canagliflozin) have shown significant renal protective effects in both diabetic and non-diabetic CKD. They reduce intraglomerular pressure through tubuloglomerular feedback, decrease albuminuria, slow GFR decline, and reduce risk of kidney failure. They are now recommended for CKD patients with or without diabetes when eGFR ≥20 mL/min/1.73m².",
            
            "Nephrotic syndrome is characterized by heavy proteinuria (>3.5 g/day or protein/creatinine ratio >300 mg/mmol), hypoalbuminemia (<3.0 g/dL), edema, and hyperlipidemia. Common causes include minimal change disease, focal segmental glomerulosclerosis (FSGS), membranous nephropathy, and diabetic nephropathy. Complications include thromboembolism, infections, acute kidney injury, and hyperlipidemia.",
            
            "Hypertension management in CKD requires individualized approach. Target blood pressure is generally <130/80 mmHg for most CKD patients. First-line agents include ACEi/ARBs for proteinuric CKD, calcium channel blockers for non-proteinuric CKD or as add-on therapy, and thiazide or loop diuretics for volume management. Multiple agents are often required.",
            
            "Anemia of CKD typically develops when eGFR falls below 60 mL/min/1.73m². It results from decreased erythropoietin production, iron deficiency, chronic inflammation, and shortened red blood cell survival. Management includes iron supplementation (target ferritin >100 ng/mL, TSAT >20%), erythropoiesis-stimulating agents (ESAs) with hemoglobin target 10-11.5 g/dL, and treatment of other contributing factors.",
            
            "CKD-Mineral and Bone Disorder (CKD-MBD) involves abnormalities in calcium, phosphorus, PTH, and vitamin D metabolism. As GFR declines, phosphorus retention occurs, leading to secondary hyperparathyroidism. Management includes dietary phosphorus restriction, phosphate binders (calcium-based, sevelamer, lanthanum), vitamin D supplementation, and calcimimetics (cinacalcet) if needed.",
            
            "Medication management in CKD requires dose adjustments for many drugs. Renally cleared medications requiring adjustment include metformin (contraindicated if eGFR <30), gabapentin, allopurinol, many antibiotics (aminoglycosides, vancomycin, fluoroquinolones), and digoxin. NSAIDs should generally be avoided due to risk of AKI and progression. Always check dosing references.",
            
            "Contrast-induced nephropathy (CIN) is AKI occurring 48-72 hours after contrast exposure, defined as increase in serum creatinine ≥0.5 mg/dL or ≥25% from baseline. Risk factors include pre-existing CKD, diabetes, volume depletion, high contrast volume, and concurrent nephrotoxins. Prevention includes IV isotonic saline hydration (1 mL/kg/h for 12 hours before and after), using lowest contrast volume, holding nephrotoxins, and avoiding repeat exposures.",
            
            "Hemodialysis is typically initiated when eGFR <10-15 mL/min/1.73m² with uremic symptoms, refractory volume overload, refractory hyperkalemia, metabolic acidosis, or pericarditis. Access options include arteriovenous fistula (preferred, created months before anticipated need), arteriovenous graft, or tunneled dialysis catheter. Typical prescription is 3-4 hours three times weekly.",
            
            "Peritoneal dialysis involves instilling dialysate into the peritoneal cavity using the peritoneal membrane as the dialyzer. Modalities include continuous ambulatory PD (CAPD) with manual exchanges 3-4 times daily, or automated PD (APD) with cycler overnight. Advantages include home-based therapy, better preservation of residual renal function, and hemodynamic stability. Complications include peritonitis, catheter infections, and membrane failure.",
            
            "Kidney transplantation offers superior survival and quality of life compared to dialysis. Living donor transplants have better outcomes than deceased donor. Post-transplant immunosuppression typically includes induction (basiliximab or ATG) and maintenance with tacrolimus or cyclosporine, mycophenolate, and prednisone. Complications include acute and chronic rejection, infections, medication toxicity, and recurrent disease.",
            
            "Lupus nephritis occurs in 30-50% of SLE patients. WHO classification includes Class I minimal mesangial, Class II mesangial proliferative, Class III focal, Class IV diffuse proliferative, Class V membranous, and Class VI advanced sclerosing. Treatment depends on class but may include corticosteroids, mycophenolate mofetil, cyclophosphamide, or rituximab. Response monitoring includes proteinuria, serum creatinine, and serologies.",
            
            "IgA nephropathy is the most common primary glomerulonephritis worldwide. Presentation varies from asymptomatic hematuria to rapidly progressive GN. Triggers often include upper respiratory infections. Pathology shows mesangial IgA deposition. Treatment includes ACEi/ARBs for blood pressure and proteinuria control, immunosuppression for progressive disease with crescents or severe proteinuria, and fish oil (omega-3 fatty acids).",
            
            "Polycystic kidney disease (PKD) is genetic disorder causing bilateral kidney cysts. Autosomal dominant PKD (ADPKD) is most common, caused by PKD1 or PKD2 mutations. Manifestations include hypertension, hematuria, cyst infections, nephrolithiasis, and progressive kidney dysfunction. Management includes blood pressure control, pain management, tolvaptan to slow cyst growth, and family screening. ESRD typically occurs in 40s-60s.",
            
            "Uremic syndrome occurs when kidney function severely deteriorates, causing accumulation of toxins. Symptoms include fatigue, nausea/vomiting, anorexia, pruritus, metallic taste, cognitive impairment, peripheral neuropathy, and pericarditis. Uremic frost (crystallized urea on skin) is rare but pathognomonic. These symptoms indicate need for dialysis initiation, typically when eGFR <10-15 mL/min/1.73m² with symptoms refractory to medical management."
        ]
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Add documents to vector database with embeddings"""
        try:
            if not documents:
                system_logger.log_error("vector_db", "No documents to add")
                return False
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(
                documents,
                show_progress_bar=True,
                convert_to_numpy=True
            ).tolist()
            
            # Generate IDs
            existing_count = self.collection.count()
            ids = [f"doc_{existing_count + i}" for i in range(len(documents))]
            
            # Prepare metadatas
            if metadatas is None:
                metadatas = [
                    {
                        "source": "Comprehensive Clinical Nephrology",
                        "type": "medical_textbook",
                        "chunk_index": i
                    }
                    for i in range(len(documents))
                ]
            
            # Add to collection in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_end = min(i + batch_size, len(documents))
                
                self.collection.add(
                    embeddings=embeddings[i:batch_end],
                    documents=documents[i:batch_end],
                    metadatas=metadatas[i:batch_end],
                    ids=ids[i:batch_end]
                )
            
            system_logger.log_system_event(
                "documents_added",
                {
                    "num_documents": len(documents),
                    "collection": settings.CHROMA_COLLECTION_NAME
                }
            )
            
            return True
            
        except Exception as e:
            system_logger.log_error(
                "vector_db",
                f"Error adding documents: {e}"
            )
            return False
    
    def search(
        self,
        query: str,
        n_results: int = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents using semantic search"""
        n_results = n_results or settings.TOP_K_RESULTS
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=min(n_results, self.collection.count())
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else None
                    })
            
            system_logger.log_rag_query(
                query,
                len(formatted_results),
                True,
                [r['metadata'].get('source', 'Unknown') for r in formatted_results]
            )
            
            return formatted_results
            
        except Exception as e:
            system_logger.log_error(
                "vector_db",
                f"Error searching documents: {e}"
            )
            system_logger.log_rag_query(query, 0, False)
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                "document_count": count,
                "collection_name": settings.CHROMA_COLLECTION_NAME,
                "embedding_model": settings.EMBEDDINGS_MODEL
            }
        except Exception as e:
            system_logger.log_error(
                "vector_db",
                f"Error getting collection stats: {e}"
            )
            return {"document_count": 0}
    
    def initialize_from_pdf(self, pdf_path: Optional[str] = None) -> bool:
        """Initialize vector database from PDF if empty"""
        try:
            current_count = self.collection.count()
            
            if current_count > 0:
                system_logger.log_system_event(
                    "vector_db_already_initialized",
                    {"document_count": current_count}
                )
                return True
            
            # Process PDF
            chunks = self.process_pdf(pdf_path)
            
            if not chunks:
                system_logger.log_error(
                    "vector_db",
                    "No chunks extracted from PDF"
                )
                return False
            
            # Add documents
            success = self.add_documents(chunks)
            
            if success:
                system_logger.log_system_event(
                    "vector_db_initialized_from_pdf",
                    {"document_count": len(chunks)}
                )
            
            return success
            
        except Exception as e:
            system_logger.log_error(
                "vector_db",
                f"Error initializing from PDF: {e}"
            )
            return False
