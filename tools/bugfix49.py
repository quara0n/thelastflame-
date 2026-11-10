# Versjon 49: to feil robottesteren fant i versjon 48 (tråden «Automate game testing»).
# 1. Spillet frøs for godt hvis Testbenk-fanen var åpen når byggetiden gikk ut: wave 15 hadde ingen ny art
#    (gresshoppene kom alt i wave 13), og wave-lista i Testbenk krasjet på det. Wave 13 er nå bare Thornlings, så
#    hver wave har en ny art igjen, og Testbenk tåler en wave uten.
# 2. Skyttere med ordre «Fremover» gikk ut av kartet når ingen nærkamp-units var igjen (de fulgte en front som ikke
#    fantes). Nå skyter de på nærmeste fiende, eller går hjem når det ikke er noen.
from patch import sub

def apply(s):
    s = sub(s, "  { style: 'Tornkratt', groups: [['thornling', 28, 'front'], ['locust', 12, 'flank']], world: 2 },",
               "  { style: 'Tornkratt', groups: [['thornling', 40, 'front']], world: 2 },")
    s = sub(s, "${w.n} · ${TYPES[w.newType].name}${w.boss ? ' (boss)' : ''}",
               "${w.n} · ${(TYPES[w.newType] || TYPES[w.groups[0][0]]).name}${w.boss ? ' (boss)' : ''}")
    s = sub(s, "      const front = this._frontZ();\n      const tz = front == null ? u.z - 3 : Math.max(front + 1.5, Math.min(u.z, u.homeZ) - 3);\n",
               "      const front = this._frontZ();\n"
               "      if (front == null) { if (this._engage(u, enemies, attackers, dt, 80)) return; this._returnHome(u, dt); return; }\n"
               "      const tz = Math.max(front + 1.5, Math.min(u.z, u.homeZ) - 3);\n")
    return s
