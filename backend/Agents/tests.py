from Agents.extraction_agent import ExtractionAgent
from dotenv import load_dotenv
from Agents.models import QuestionExtractionModel,AnswerExtractionModel
import pytest 

@pytest.mark.asyncio
async def test_question_extraction_return_type():
    load_dotenv()
    questions = """
    1. What is cloud computing, and how does it differ from traditional computing? (5 marks)
    2. Explain the main service models of cloud computing: IaaS, PaaS, and SaaS. (6 marks)
    3. Describe the key benefits of using cloud computing for businesses. (4 marks)
    4. How does virtualization support cloud computing infrastructure? (5 marks)
    5. Differentiate between public, private, and hybrid cloud deployment models. (6 marks)
    6. What are the major security challenges in cloud computing, and how can they be mitigated? (7 marks)
    7. Explain how scalability works in the cloud. What is auto-scaling? (5 marks)
    8. What is serverless computing, and what are its advantages and disadvantages? (6 marks)
    9. How do cloud providers ensure data availability, fault tolerance, and redundancy? (5 marks)
    10. List and briefly describe any three popular cloud platforms and one key service offered by each. (6 marks)
    """
    agent = ExtractionAgent()
    output = await agent.extract_questions(questions)
    assert isinstance(output, list), "Expected a list"

    assert output, "Expected at least one question"
    for item in output:
        assert isinstance(item, QuestionExtractionModel), (
            f"Expected QuestionExtractionModel, " 
            f"got {type(item)} with content {item!r}"
        )
    print(output)
    
@pytest.mark.asyncio
async def test_answer_extraction_return_type():
    load_dotenv()
    answers = """
    1. What is cloud computing, and how does it differ from traditional computing? (5 marks)
    Cloud computing delivers computing resources—like servers, storage, databases, networking, and software—over the internet (“the cloud”) on a pay-as-you-go model. Unlike traditional on-premises setups, cloud computing offers on-demand scaling, minimal capital investment, and managed infrastructure maintenance.

    2. Explain the main service models of cloud computing: IaaS, PaaS, and SaaS. (6 marks)
    - IaaS (Infrastructure as a Service): Provides virtual machines, networks, and storage (e.g. AWS EC2).
    - PaaS (Platform as a Service): Offers runtime environments and development tools (e.g. Azure App Services).
    - SaaS (Software as a Service): Delivers fully managed applications to end users via the internet (e.g. Gmail or Office 365).

    3. Describe the key benefits of using cloud computing for businesses. (4 marks)
    Cost-efficiency (no upfront infrastructure cost); scalability and elasticity; faster time-to-market; global access and collaboration; enhanced reliability through built-in redundancy and backups.

    4. How does virtualization support cloud computing infrastructure? (5 marks)
    Virtualization creates multiple virtual machines on a single physical server, allowing dynamic resource allocation, efficient utilization, and quick provisioning of isolated environments.

    5. Differentiate between public, private, and hybrid cloud deployment models. (6 marks)
    - Public cloud: Shared infrastructure provided over the internet (e.g. AWS, GCP).
    - Private cloud: Dedicated infrastructure for one organization, either on-prem or hosted.
    - Hybrid cloud: A mix of public and private, enabling data and workload portability between environments.

    6. What are the major security challenges in cloud computing, and how can they be mitigated? (7 marks)
    Challenges include data breaches, misconfigured services, insider threats, and weak identity controls. Mitigation strategies: encryption at rest and in transit, robust IAM and zero-trust policies, regular audits, and proper configuration management.

    7. Explain how scalability works in the cloud. What is auto-scaling? (5 marks)
    Scalability allows resources to increase or decrease with demand. Auto-scaling automatically adjusts compute capacity based on defined metrics like CPU usage or traffic, ensuring cost-efficiency and performance.

    8. What is serverless computing, and what are its advantages and disadvantages? (6 marks)
    Serverless (Function-as-a-Service) allows running code without managing servers.  
    Advantages: no server management, automatic scaling, pay-per-use.  
    Disadvantages: possible cold-start latency, limited execution time, less control over environment, potential vendor lock-in.

    9. How do cloud providers ensure data availability, fault tolerance, and redundancy? (5 marks)
    They replicate data and services across multiple zones and regions, use failover strategies, provide automated backups, and maintain disaster-recovery setups.

    10. List and briefly describe any three popular cloud platforms and one key service offered by each. (6 marks)
    - AWS: Offers EC2 for virtual machines.  
    - Microsoft Azure: Provides Azure Virtual Machines for hybrid and enterprise workloads.  
    - Google Cloud Platform: Supplies Cloud Storage for scalable, global object storage.
    """

    agent = ExtractionAgent()
    output = await agent.extract_answers(answers)
    assert isinstance(output,list), "Expected a list"
    assert output, "Expected at least one question"
    for item in output:
        assert isinstance(item, AnswerExtractionModel), (
            f"Expected QuestionExtractionModel, " 
            f"got {type(item)} with content {item!r}"
        )
    print(output)
    
        

    
