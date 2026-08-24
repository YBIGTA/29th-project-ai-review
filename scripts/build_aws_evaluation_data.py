from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data/processed/aws.json"
RUBRIC_PATH = ROOT / "data/evaluation/rubrics/aws.json"


def T(i, ko, en="", abbr=None, aliases=None):
    return {"term_id": i, "canonical_ko": ko, "canonical_en": en, "abbreviations": abbr or [], "accepted_aliases": aliases or [], "symbols": [], "not_equivalent_to": []}


TERMINOLOGY = [
    T("cloud_computing", "클라우드 컴퓨팅", "cloud computing"), T("on_premises", "온프레미스", "on-premises", aliases=["온프레미스 환경"]), T("on_demand", "온디맨드", "on-demand"),
    T("iaas", "서비스형 인프라", "Infrastructure as a Service", ["IaaS"]), T("paas", "서비스형 플랫폼", "Platform as a Service", ["PaaS"]), T("saas", "서비스형 소프트웨어", "Software as a Service", ["SaaS"]),
    T("shared_responsibility", "공동 책임 모델", "shared responsibility model"), T("elasticity", "탄력성", "elasticity"), T("scalability", "확장성", "scalability"), T("scale_up", "스케일 업", "scale up"), T("scale_down", "스케일 다운", "scale down"),
    T("auto_scaling", "오토 스케일링", "Auto Scaling"), T("pay_as_you_go", "사용량 기반 과금", "pay as you go"), T("cloud_migration", "클라우드 마이그레이션", "cloud migration"), T("devops", "데브옵스", "DevOps"), T("cicd", "지속적 통합·배포", "continuous integration and delivery", ["CI/CD"]), T("monitoring", "모니터링", "monitoring"),
    T("aws", "아마존 웹 서비스", "Amazon Web Services", ["AWS"]), T("ec2", "EC2", "Elastic Compute Cloud", ["EC2"]), T("s3", "S3", "Simple Storage Service", ["S3"]), T("rds", "RDS", "Relational Database Service", ["RDS"]), T("lambda", "람다", "AWS Lambda"), T("vpc", "가상 사설 클라우드", "Virtual Private Cloud", ["VPC"]), T("iam", "자격 증명 및 접근 관리", "Identity and Access Management", ["IAM"]),
    T("instance", "인스턴스", "instance"), T("ami", "아마존 머신 이미지", "Amazon Machine Image", ["AMI"]), T("ebs", "탄력적 블록 스토어", "Elastic Block Store", ["EBS"]), T("load_balancer", "로드 밸런서", "load balancer"), T("elb", "Elastic Load Balancing", "Elastic Load Balancing", ["ELB"]),
    T("security_group", "보안 그룹", "security group"), T("inbound", "인바운드", "inbound"), T("outbound", "아웃바운드", "outbound"), T("least_privilege", "최소 권한", "least privilege"), T("ssh", "보안 셸", "Secure Shell", ["SSH"]), T("http", "HTTP", "Hypertext Transfer Protocol", ["HTTP"]), T("https", "HTTPS", "Hypertext Transfer Protocol Secure", ["HTTPS"]), T("tls", "전송 계층 보안", "Transport Layer Security", ["TLS"]), T("mixed_content", "혼합 콘텐츠", "mixed content"), T("tcp", "전송 제어 프로토콜", "Transmission Control Protocol", ["TCP"]), T("udp", "사용자 데이터그램 프로토콜", "User Datagram Protocol", ["UDP"]), T("dns", "도메인 이름 시스템", "Domain Name System", ["DNS"]), T("route53", "Route 53", "Amazon Route 53"),
    T("public_ip", "공인 IP", "public IP"), T("private_ip", "사설 IP", "private IP"), T("subnet", "서브넷", "subnet"), T("cidr", "클래스 없는 도메인 간 라우팅", "Classless Inter-Domain Routing", ["CIDR"]), T("docker_image", "Docker 이미지", "Docker image"), T("registry", "이미지 레지스트리", "image registry")]

TITLES = ["AWS 표지", "강의 목차", "Cloud Computing", "온프레미스의 한계", "클라우드와 서비스 모델", "클라우드와 온프레미스 비교", "공동 책임 모델", "클라우드 전환 절차", "클라우드와 DevOps", "클라우드의 탄력성과 자동화", "AWS와 네트워크", "AWS 소개", "AWS 서비스 개요", "EC2·S3·RDS", "EC2 핵심 구성", "EC2 콘솔", "인스턴스·AMI·EBS·ELB", "보안 그룹", "SSH·HTTP·HTTPS", "TCP·UDP와 포트", "IP·VPC·Subnet·CIDR", "Docker를 이용한 배포", "웹 배포 실습", "DB 배포 실습", "강의 마무리"]
CONTENT = {
1:"AWS 강의 표지이다.",2:"강의는 클라우드 컴퓨팅, AWS와 네트워크 복습, 웹 배포 실습, DB 배포 실습 순으로 구성된다.",3:"클라우드 컴퓨팅 섹션의 구분 페이지이다.",
4:"온프레미스는 서버를 직접 구매·설치·유지해야 하므로 초기 비용과 용량 예측 부담이 크고, 수요 변화에 신속히 대응하기 어렵다.",
5:"클라우드 컴퓨팅은 인터넷을 통해 컴퓨팅 자원을 필요할 때 사용하고 사용량에 따라 비용을 지불하는 방식이다. IaaS·PaaS·SaaS는 공급자가 관리하는 범위가 서로 다르다.",
6:"온프레미스는 물리 인프라와 운영을 직접 통제하지만 조달·확장 부담이 크다. 클라우드는 자원을 빠르게 만들고 탄력적으로 조정할 수 있으나 비용·보안·책임 범위를 관리해야 한다.",
7:"공동 책임 모델에서 IaaS 사용자는 OS부터 애플리케이션·데이터까지 더 넓게 관리한다. PaaS는 플랫폼 운영을 공급자가 맡고 사용자는 주로 애플리케이션과 데이터를, SaaS는 공급자가 전체 스택을 운영하고 사용자는 서비스를 이용한다.",
8:"클라우드 전환은 현황 평가와 계획, 적합한 서비스·구조 선택, 데이터 이전과 시스템 통합, 테스트와 운영 최적화의 반복 과정이다.",
9:"클라우드와 DevOps는 CI/CD 자동화, 탄력적 배포, 모니터링을 결합해 개발·배포·운영의 반복 속도와 안정성을 높인다.",
10:"클라우드의 탄력성은 수요에 맞춰 자원을 늘리고 줄이는 능력이다. Auto Scaling, 사용량 기반 과금, 모니터링과 자동화가 이를 지원하며 scale up/down과 서버 수 조정은 구분해야 한다.",
11:"AWS와 네트워크 복습 섹션의 구분 페이지이다.",12:"AWS는 다양한 클라우드 인프라와 관리형 서비스를 제공하는 플랫폼이다.",
13:"EC2는 가상 서버, S3는 객체 저장소, RDS는 관리형 관계형 DB, Lambda는 서버리스 함수 실행, VPC는 논리적 네트워크, IAM은 인증·권한 관리를 담당한다. 장애 영향은 서비스 의존성과 Region·AZ를 포함한 구조에 따라 달라진다.",
14:"EC2·S3·RDS는 각각 compute, object storage, managed relational database 역할을 하는 대표 서비스다.",
15:"EC2 instance는 가상 서버다. AMI는 OS와 소프트웨어 구성을 담은 실행 template이고 Auto Scaling은 수요에 맞춰 instance 수를 조정하며 ELB는 여러 target으로 traffic을 분산한다.",
16:"EC2 console에서 instance와 관련 자원을 확인하는 화면이다.",
17:"AMI로 일관된 instance를 만들고 EBS를 network-attached block storage로 연결한다. EBS의 수명은 delete-on-termination 설정 등에 따라 instance와 독립적으로 유지될 수 있다. Load balancer는 여러 backend로 요청을 분산한다.",
18:"Security group은 instance 등 resource에 적용되는 stateful virtual firewall이다. Inbound와 outbound rule에 protocol·port·source 또는 destination을 지정하며 필요한 통신만 허용하는 least privilege를 적용한다.",
19:"SSH는 원격 shell 접속, HTTP는 암호화되지 않은 web 통신, HTTPS는 TLS로 보호된 HTTP다. Mixed content는 HTTPS page가 HTTP resource를 불러올 때 발생하며 모든 resource URL과 전달 경로를 HTTPS로 구성해야 한다.",
20:"TCP는 연결과 신뢰성 있는 byte stream을 제공하고 UDP는 연결 설정 없이 datagram을 전달한다. SSH 22, HTTP 80, HTTPS 443이 대표 port이며 DNS는 TCP와 UDP를 모두 사용할 수 있다. Protocol은 application 요구에 맞춰 선택한다.",
21:"VPC는 논리적으로 격리된 network이고 subnet은 CIDR address range로 나눈 구역이다. Public·private IP와 route, internet gateway, security control을 함께 구성해야 실제 외부 통신 가능 여부가 정해진다.",
22:"Local에서 Docker image를 build해 registry에 push하고 EC2 등 server에서 pull·run하는 배포 흐름이다. Runtime 설정, port, network, secret과 persistent data는 image와 별도로 관리한다.",
23:"웹 애플리케이션 배포 실습의 구분 페이지이다.",24:"데이터베이스 배포 실습의 구분 페이지이다.",25:"AWS 강의 종료 페이지이다."}
DIV={3,11,23,24}; ROLES={1:"cover",2:"table_of_contents",25:"closing",**{p:"section_divider" for p in DIV}}
def cur(p):
    role=ROLES.get(p,"core_content"); title=TITLES[p-1]
    return [{"topic":title,"concepts":[title],"visual_description":f"{title}의 구조·서비스·흐름을 도식과 예시로 제시한다." if role=="core_content" else f"{title} 페이지이다.","content":CONTENT[p]}]
CURATION={p:cur(p) for p in range(1,26)}

def U(i,p,k,q,x,ts,st="text"):
    return {"unit_id":i,"page":p,"type":k,"source_type":st,"source_excerpt":q,"normalized_explanation":x,"source_status":"verified","term_ids":ts}
UNITS=[
U("aws_p4_onprem",4,"comparison","직접 서버를 구매하고 관리 / 초기 비용 / 확장에 시간","On-premises는 직접 인프라를 소유·운영해 초기 비용과 capacity planning 부담이 크다.",["on_premises","cloud_computing"]),
U("aws_p5_cloud",5,"definition","필요한 만큼 IT 자원을 인터넷을 통해 사용 / IaaS PaaS SaaS","Cloud computing과 service model을 설명한다.",["cloud_computing","on_demand","pay_as_you_go","iaas","paas","saas"]),
U("aws_p7_responsibility",7,"comparison","IaaS / PaaS / SaaS 관리 범위","Service model별 provider와 customer의 책임 범위가 다르다.",["shared_responsibility","iaas","paas","saas"],"visual"),
U("aws_p8_migration",8,"procedure","계획 및 평가 / 선택 및 최적화 / 데이터 이전 / 통합 / 테스트","Cloud migration은 평가부터 test·optimization까지 이어진다.",["cloud_migration","cloud_computing"]),
U("aws_p9_devops",9,"relation","CI/CD / 탄력적 확장 / 모니터링 / 자동화","Cloud와 DevOps automation의 관계다.",["devops","cicd","monitoring","elasticity"]),
U("aws_p10_elasticity",10,"relation","Scale up/down / Auto Scaling / Pay as you go","Demand에 따라 resource를 조정하고 사용량 기준으로 과금한다.",["elasticity","scalability","scale_up","scale_down","auto_scaling","pay_as_you_go"]),
U("aws_p13_services",13,"comparison","EC2 / S3 / RDS / Lambda / VPC / IAM","AWS service별 역할을 구분한다.",["aws","ec2","s3","rds","lambda","vpc","iam"]),
U("aws_p15_ec2",15,"relation","Instance / AMI / Auto Scaling / ELB","EC2 compute와 template, scaling, traffic distribution 관계다.",["ec2","instance","ami","auto_scaling","elb","load_balancer"]),
U("aws_p17_storage_lb",17,"relation","Instance / Image / EBS / Load Balancing","AMI·EBS·load balancer가 instance와 연결된다.",["instance","ami","ebs","load_balancer","elb"],"visual"),
U("aws_p18_sg",18,"procedure","Inbound / Outbound / 필요한 포트만 허용","Security group rule과 least privilege를 설명한다.",["security_group","inbound","outbound","least_privilege"]),
U("aws_p19_web_protocol",19,"warning","SSH / HTTP / HTTPS / Mixed Content","Remote access와 encrypted web traffic, mixed content를 구분한다.",["ssh","http","https","tls","mixed_content"]),
U("aws_p20_transport",20,"comparison","TCP / UDP / SSH 22 / HTTP 80 / HTTPS 443 / DNS","Transport protocol과 application port를 구분한다.",["tcp","udp","ssh","http","https","dns","route53"]),
U("aws_p21_network",21,"relation","Public IP / Private IP / VPC / Subnet / CIDR","VPC address space와 subnet, IP 범위를 연결한다.",["public_ip","private_ip","vpc","subnet","cidr"]),
U("aws_p22_deploy",22,"procedure","docker build / push / pull / run","Docker image registry를 통한 cloud deployment 흐름이다.",["docker_image","registry","ec2"])]

MAP={
"aws.onprem_cloud":["aws_p4_onprem"],"aws.cloud_definition":["aws_p5_cloud"],"aws.service_models":["aws_p7_responsibility"],"aws.shared_responsibility":["aws_p7_responsibility"],"aws.migration":["aws_p8_migration"],"aws.devops":["aws_p9_devops"],"aws.elasticity":["aws_p10_elasticity"],"aws.cost_scaling":["aws_p10_elasticity"],
"aws.services":["aws_p13_services"],"aws.compute_storage_db":["aws_p13_services"],"aws.identity_network":["aws_p13_services"],"aws.instance_ami":["aws_p15_ec2","aws_p17_storage_lb"],"aws.ebs":["aws_p17_storage_lb"],"aws.autoscaling_elb":["aws_p15_ec2"],"aws.availability":["aws_p13_services"],
"aws.security_group":["aws_p18_sg"],"aws.least_privilege":["aws_p18_sg"],"aws.web_protocols":["aws_p19_web_protocol"],"aws.mixed_content":["aws_p19_web_protocol"],"aws.transport":["aws_p20_transport"],"aws.ports":["aws_p20_transport"],"aws.vpc_subnet":["aws_p21_network"],"aws.public_private":["aws_p21_network"],"aws.cidr":["aws_p21_network"],"aws.docker_deploy":["aws_p22_deploy"],"aws.runtime_config":["aws_p22_deploy"]}
ERR={
"aws.service_models":["IaaS·PaaS·SaaS에서 사용자와 공급자의 책임 범위가 모두 같다고 설명"],"aws.shared_responsibility":["Cloud provider가 application data와 access 설정까지 언제나 전적으로 책임진다고 설명"],"aws.elasticity":["Elasticity가 수요와 무관하게 자원을 항상 최대치로 유지하는 것이라고 설명"],"aws.services":["EC2·S3·RDS의 역할을 서로 뒤바꿔 설명"],"aws.ebs":["EBS를 S3와 같은 object storage라고 설명"],"aws.availability":["AWS의 일부 장애가 모든 Region과 모든 architecture를 반드시 동시에 중단시킨다고 설명"],"aws.security_group":["Security group의 inbound와 outbound 방향을 반대로 설명"],"aws.least_privilege":["Outbound 전체 허용이 모든 system에서 언제나 가장 안전하다고 단정"],"aws.mixed_content":["Load balancer만 추가하면 HTTP resource URL을 고치지 않아도 mixed content가 자동 해결된다고 설명"],"aws.transport":["AWS application은 UDP를 사용할 수 없고 언제나 TCP만 선택해야 한다고 설명"],"aws.public_private":["Public IP만 있으면 route와 security rule에 상관없이 누구나 반드시 접속할 수 있다고 설명"]}
def C(i,r,x,cat="explanation_application"): return {"claim_id":i,"role":r,"category":cat,"text":x,"weight":1.0,"evidence":[],"term_ids":[],"evaluation_criteria":{"required_elements":[x],"critical_errors":ERR.get(i,[])}}
def S(i,t,x,c): return {"sub_objective_id":i,"title":t,"summary":x,"claims":c}
def O(i,t,x,s):
    n=sum(len(v["claims"]) for v in s); return {"objective_id":i,"title":t,"selection_description":x,"supporting_claim_slots":2 if n<=8 else 3,"sub_objectives":s}
def build_rubric():
    o=[
    O("aws.cloud_foundations","클라우드 컴퓨팅과 서비스 모델","온프레미스와 클라우드, 책임·탄력성·전환을 설명한다.",[
      S("aws.cloud.concept","온프레미스와 클라우드","운영 방식과 비용 구조를 비교한다.",[C("aws.onprem_cloud","essential","On-premises는 infrastructure를 직접 구매·운영해 초기 비용과 capacity planning 부담이 크고 cloud는 on-demand resource와 pay-as-you-go로 빠르게 조정할 수 있다.","core_understanding"),C("aws.cloud_definition","supporting","Cloud computing은 network를 통해 compute·storage 같은 IT resource를 필요할 때 제공받는 방식이다.")]),
      S("aws.cloud.models","서비스 모델과 책임","IaaS·PaaS·SaaS를 구분한다.",[C("aws.service_models","essential","IaaS·PaaS·SaaS는 provider가 관리하는 stack 범위가 차례로 넓어지고 customer가 직접 관리하는 범위는 줄어든다."),C("aws.shared_responsibility","supporting","Cloud에서도 customer는 선택한 service model에 따라 data·application·OS·access configuration 등 자신의 책임을 수행해야 한다.")]),
      S("aws.cloud.operations","전환과 DevOps","Migration과 automation을 설명한다.",[C("aws.migration","essential","Cloud migration은 workload 평가·계획, service와 architecture 선택, data 이전·통합, test·optimization의 단계로 진행한다."),C("aws.devops","supporting","Cloud resource와 DevOps CI/CD·monitoring·automation을 결합하면 반복 배포와 운영 대응을 빠르게 할 수 있다.")]),
      S("aws.cloud.scaling","탄력성과 비용","수요 기반 조정을 설명한다.",[C("aws.elasticity","essential","Elasticity는 demand 변화에 맞춰 resource를 자동 또는 수동으로 늘리고 줄이는 능력이며 Auto Scaling이 이를 지원한다."),C("aws.cost_scaling","supporting","Pay-as-you-go는 실제 사용 resource에 따라 비용을 지불하게 하지만 monitoring과 right-sizing 없이 비용 효율이 자동 보장되지는 않는다.")])]),
    O("aws.services_compute","AWS 서비스와 EC2 운영","대표 서비스와 EC2 구성·가용성을 설명한다.",[
      S("aws.service.selection","서비스 역할","서비스를 요구사항에 연결한다.",[C("aws.services","essential","EC2는 virtual compute, S3는 object storage, RDS는 managed relational database, Lambda는 event-driven serverless compute, VPC는 network, IAM은 identity·permission을 담당한다.","core_understanding"),C("aws.compute_storage_db","supporting","Compute·storage·database 요구를 구분해 EC2·S3·RDS 등 적합한 service를 선택한다."),C("aws.identity_network","supporting","VPC는 workload의 logical network boundary를 구성하고 IAM은 user·role·policy로 AWS resource access를 제어한다.")]),
      S("aws.ec2.resources","EC2와 저장소","Instance·AMI·EBS를 연결한다.",[C("aws.instance_ami","essential","EC2 instance는 virtual server이고 AMI는 OS·software configuration을 담아 instance를 일관되게 생성하는 template다."),C("aws.ebs","supporting","EBS는 EC2에 network로 attach하는 block storage이며 설정에 따라 instance 종료 후에도 volume을 보존할 수 있다.")]),
      S("aws.ec2.scale","확장과 부하 분산","Server 수와 traffic을 설명한다.",[C("aws.autoscaling_elb","essential","Auto Scaling은 policy와 demand에 따라 instance 수를 조정하고 ELB는 healthy target들에 traffic을 분산한다."),C("aws.availability","supporting","Cloud availability는 Region·Availability Zone·service dependency와 redundancy architecture에 달려 있어 단일 장애가 모든 AWS workload를 동일하게 중단시키는 것은 아니다.")])]),
    O("aws.network_security_deployment","네트워크·보안·배포","접근 제어, protocol, VPC와 image 배포를 설명한다.",[
      S("aws.net.security","보안 그룹","Traffic rule과 최소 권한을 설명한다.",[C("aws.security_group","essential","Security group은 stateful virtual firewall로 inbound는 resource로 들어오는 traffic, outbound는 resource에서 나가는 traffic rule이다.","core_understanding"),C("aws.least_privilege","supporting","Inbound와 outbound 모두 application에 필요한 protocol·port·source 또는 destination만 허용하는 least privilege를 목표로 한다.")]),
      S("aws.net.protocol","Web·전송 프로토콜","SSH·HTTP(S)와 TCP·UDP를 구분한다.",[C("aws.web_protocols","essential","SSH는 remote shell, HTTP는 unencrypted web protocol, HTTPS는 HTTP를 TLS로 보호한 protocol이다."),C("aws.mixed_content","supporting","Mixed content는 HTTPS page가 HTTP resource를 요청할 때 생기므로 page와 asset·API URL을 모두 HTTPS로 제공해야 한다."),C("aws.transport","supporting","TCP는 reliable ordered byte stream, UDP는 connectionless datagram이며 application requirement에 맞춰 선택한다."),C("aws.ports","supporting","SSH 22, HTTP 80, HTTPS 443은 대표 default port이고 DNS는 상황에 따라 UDP와 TCP를 사용한다.")]),
      S("aws.net.vpc","VPC와 주소","논리 network와 외부 연결 조건을 설명한다.",[C("aws.vpc_subnet","essential","VPC는 isolated logical network이고 subnet은 VPC CIDR 범위의 일부로 workload를 구역화한다."),C("aws.public_private","supporting","Public·private IP 구분만으로 connectivity가 결정되지 않으며 route table, internet gateway, security group 등도 함께 충족해야 한다."),C("aws.cidr","supporting","CIDR은 IP address prefix와 network 크기를 표현해 VPC와 subnet address range를 정의한다.")]),
      S("aws.net.deploy","Container 배포","Image 전달 흐름을 설명한다.",[C("aws.docker_deploy","essential","Local에서 Docker image를 build해 registry에 push하고 cloud server에서 pull·run한다."),C("aws.runtime_config","supporting","Secret·port·network와 persistent data 같은 runtime configuration은 reusable image에 고정하지 않고 deployment environment에서 안전하게 주입한다.")])])]
    return {"schema_version":"2.2.0","lecture_id":"aws","lecture_name":"AWS","assessment":{"mode":"selected_topic_recall","target_seconds":120,"max_seconds":120,"score_policy":{"essential_points":60,"supporting_points":20,"coverage_points":20}},"top_level_objectives":o,"excluded_source_claims":[{"page":13,"chunk_id":"aws_p13_01","source_text":"AWS가 다운되면 다 다운","reason":"장애 범위는 Region·AZ·service dependency와 redundancy architecture에 따라 달라짐"},{"page":18,"chunk_id":"aws_p18_01","source_text":"Outbound는 보통 전체 허용","reason":"일반적 default일 수 있으나 모든 workload의 최선 보안 정책으로 일반화하지 않음"},{"page":19,"chunk_id":"aws_p19_01","source_text":"Mixed Content → load balancer로 감싼다","reason":"Load balancer만으로 HTTP resource URL이 자동 수정되지 않으며 end-to-end HTTPS 구성이 필요"},{"page":20,"chunk_id":"aws_p20_01","source_text":"AWS에서는 TCP만 알면 된다 / 모르겠으면 TCP","reason":"UDP도 DNS·streaming·QUIC 등에서 사용되며 application protocol에 맞춰야 함"},{"page":21,"chunk_id":"aws_p21_01","source_text":"Public IP는 누구나 접근 가능","reason":"Public IP 외에도 route와 security control이 허용되어야 실제 접근 가능"}]}

def apply_evaluation_data(processed_path=PROCESSED_PATH,rubric_path=RUBRIC_PATH):
    d=json.loads(Path(processed_path).read_text()); pages={x["page"]:x for x in d["chunks"]}
    if set(pages)!=set(range(1,26)): raise ValueError("AWS PDF 1~25쪽이 필요합니다.")
    d["schema_version"]="2.1.0"; d["terminology"]=TERMINOLOGY
    for p in pages: pages[p].update(page_role=ROLES.get(p,"core_content"),term_ids=[],evidence_units=[],source_issues=[])
    issues={13:("aws_p13_outage","AWS가 다운되면 다 다운","overgeneralized","장애 영향은 Region·AZ·service dependency와 architecture에 따라 다르다.","exclude"),18:("aws_p18_outbound","Outbound는 보통 전체 허용","overgeneralized","Common default와 least-privilege recommendation을 구분한다.","warn"),19:("aws_p19_mixed","Mixed Content → load balancer로 감싼다","incorrect","모든 page resource와 API를 HTTPS로 제공해야 하며 LB는 TLS termination 구성 요소일 뿐이다.","exclude"),20:("aws_p20_tcp","AWS에서는 TCP만 알면 된다","incorrect","Application requirement에 따라 TCP 또는 UDP를 선택한다.","exclude"),21:("aws_p21_public","Public IP는 누구나 접근 가능","overgeneralized","Route와 security rule 등 connectivity 조건이 함께 필요하다.","warn")}
    for p,(i,s,t,c,policy) in issues.items(): pages[p]["source_issues"]=[{"issue_id":i,"source_text":s,"issue_type":t,"correction":c,"evaluation_policy":policy}]
    lookup={}
    for raw in UNITS:
        z=dict(raw); p=z.pop("page"); pages[p]["term_ids"]=list(dict.fromkeys(pages[p]["term_ids"]+z["term_ids"])); pages[p]["evidence_units"].append(z); lookup[z["unit_id"]]=(pages[p],z)
    Path(processed_path).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
    r=build_rubric(); claims={c["claim_id"]:c for o in r["top_level_objectives"] for s in o["sub_objectives"] for c in s["claims"]}
    if set(claims)!=set(MAP): raise ValueError(f"Claim mismatch: {set(claims)^set(MAP)}")
    for cid,uids in MAP.items():
        terms=[]
        for uid in uids:
            ch,u=lookup[uid]; terms+=u["term_ids"]; claims[cid]["evidence"].append({"page":ch["page"],"chunk_id":ch["chunk_id"],"unit_id":uid,"source_excerpt":u["source_excerpt"],"source_status":"verified","review_note":""})
        claims[cid]["term_ids"]=list(dict.fromkeys(terms))
    Path(rubric_path).parent.mkdir(parents=True,exist_ok=True); Path(rubric_path).write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")

if __name__=="__main__": apply_evaluation_data()
