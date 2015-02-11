import re

def name_matching_test():
    with open("cb_test.html", 'r') as f:
        result = re.findall('<h4><a title=.*? href="/organization/(.*?)"', 
            f.read())
        assert result == ['scante-net', 'inoviem-scientific', 'roadpad', 
        'lamudi-2', 'schoo', 'wandera', 'encap', 'grapevine-2', 'team8', 
        'borro', 'zig-bang', 'isignthis', 'arangodb', 'rainforest', 
        'epatientfinder', 'comparaguru', 'move-loot', 'new-matter', 
        'ppc-engine-3', 'cuckoo-workout', 'upsteem-com', 'diplomiya', 
        'zhenih-i-nevesta', 'meizu', 'iterable', 'magnum-real-estate', 
        'bear-butler', 'advicegames', 'nextracker', 'melinta', 
        'imagine-health', 'urbanstems', 'aventura', 'fetch-robotics', 
        'faaso-s', 'faaso-s', 'zdravprint', 'sight-machine', 'cell-therapy', 
        'quantum-biosystems', 'humanity', 'shopline', 'bottlenose', 
        'cinemacraft', 'mynoticeperiod-com', 'sortlist-www-sortlist-com', 
        'nodesource', 'job-forward', 'alice-app', 'listen-current', 
        'nextracker', 'lifeimage', 'advicegames', 'quantum-biosystems', 
        'gymtrack', 'listen-current', 'parklet', 'team-you-', 'bitpesa', 
        'sliide', 'digisight-technologies', 'beacon', 'fundera', 
        'studentpreneur', 'seatsmart', 'leading-mark', 'newshunt', 'topopps', 
        '51-credit-card-manager', 'vela-asia', 'pirate3d', 'anaeco', 
        'delivery-hero', 'hellofresh', 'futurpreneur', 'ulu', 'cloud-security',
         'nod', 'delta-energy---communications--llc', 'terralux', 'sensics', 
         'immedia', 'sightplan', 'adwerx', 'pet-holdings-inc', 'agenebio', 
         'agile-therapeutics', 'transcirrus-inc-', 'twinlab', 
         'snapshot-energy', 'nanthealth', 'polight', 'neumob', 'hijup-com', 
         'aurasense-therapeutics', 'appinstitute', 'g1-therapeutics', 
         'vocabulary', 'netology', 'g-predictive-gradient-gmbh']