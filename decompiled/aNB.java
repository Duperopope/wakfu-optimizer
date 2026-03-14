/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aNB
implements aqz {
    protected int o;
    protected int epc;
    protected int epd;
    protected int epe;
    protected short epf;
    protected short enc;
    protected byte epg;
    protected long eph;
    protected long epi;
    protected int epj;
    protected aND[] epk;
    protected aNC[] epl;
    protected aNE[] epm;

    public int d() {
        return this.o;
    }

    public int AK() {
        return this.epc;
    }

    public int csG() {
        return this.epd;
    }

    public int agM() {
        return this.epe;
    }

    public short csH() {
        return this.epf;
    }

    public short cqA() {
        return this.enc;
    }

    public byte csI() {
        return this.epg;
    }

    public long csJ() {
        return this.eph;
    }

    public long csK() {
        return this.epi;
    }

    public int csL() {
        return this.epj;
    }

    public aND[] csM() {
        return this.epk;
    }

    public aNC[] csN() {
        return this.epl;
    }

    public aNE[] csO() {
        return this.epm;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.epc = 0;
        this.epd = 0;
        this.epe = 0;
        this.epf = 0;
        this.enc = 0;
        this.epg = 0;
        this.eph = 0L;
        this.epi = 0L;
        this.epj = 0;
        this.epk = null;
        this.epl = null;
        this.epm = null;
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        int n2;
        this.o = aqH2.bGI();
        this.epc = aqH2.bGI();
        this.epd = aqH2.bGI();
        this.epe = aqH2.bGI();
        this.epf = aqH2.bGG();
        this.enc = aqH2.bGG();
        this.epg = aqH2.aTf();
        this.eph = aqH2.bGK();
        this.epi = aqH2.bGK();
        this.epj = aqH2.bGI();
        int n3 = aqH2.bGI();
        this.epk = new aND[n3];
        for (n2 = 0; n2 < n3; ++n2) {
            this.epk[n2] = new aND();
            this.epk[n2].a(aqH2);
        }
        n2 = aqH2.bGI();
        this.epl = new aNC[n2];
        for (n = 0; n < n2; ++n) {
            this.epl[n] = new aNC();
            this.epl[n].a(aqH2);
        }
        n = aqH2.bGI();
        this.epm = new aNE[n];
        for (int i = 0; i < n; ++i) {
            this.epm[i] = new aNE();
            ((aNe)this.epm[i]).a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oBb.d();
    }
}
