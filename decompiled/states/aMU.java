/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  aMV
 *  aMW
 *  aMX
 *  aMY
 *  aqz
 */
public class aMU
implements aqz {
    protected int o;
    protected short elG;
    protected int ciZ;
    protected int elH;
    protected int elI;
    protected short ejt;
    protected String[] elJ;
    protected int elK;
    protected short elL;
    protected byte elM;
    protected byte elN;
    protected byte elO;
    protected int elP;
    protected int elQ;
    protected boolean elR;
    protected boolean elS;
    protected boolean elT;
    protected boolean elU;
    protected short elV;
    protected byte elW;
    protected String elX;
    protected int[] elY;
    protected byte elZ;
    protected byte ema;
    protected byte emb;
    protected byte emc;
    protected float emd;
    protected float eme;
    protected byte emf;
    protected int[] egL;
    protected aMW[] emg;
    protected aMX emh;
    protected aMY emi;
    protected aMV[] emj;

    public int d() {
        return this.o;
    }

    public short cpe() {
        return this.elG;
    }

    public int aVt() {
        return this.ciZ;
    }

    public int cpf() {
        return this.elH;
    }

    public int cpg() {
        return this.elI;
    }

    public short cmL() {
        return this.ejt;
    }

    public String[] cph() {
        return this.elJ;
    }

    public int cpi() {
        return this.elK;
    }

    public short cpj() {
        return this.elL;
    }

    public byte cpk() {
        return this.elM;
    }

    public byte cpl() {
        return this.elN;
    }

    public byte cpm() {
        return this.elO;
    }

    public int cpn() {
        return this.elP;
    }

    public int cpo() {
        return this.elQ;
    }

    public boolean cpp() {
        return this.elR;
    }

    public boolean cpq() {
        return this.elS;
    }

    public boolean cpr() {
        return this.elT;
    }

    public boolean cps() {
        return this.elU;
    }

    public short cpt() {
        return this.elV;
    }

    public byte cpu() {
        return this.elW;
    }

    public String cpv() {
        return this.elX;
    }

    public int[] cpw() {
        return this.elY;
    }

    public byte cpx() {
        return this.elZ;
    }

    public byte cpy() {
        return this.ema;
    }

    public byte cpz() {
        return this.emb;
    }

    public byte cpA() {
        return this.emc;
    }

    public float cpB() {
        return this.emd;
    }

    public float cpC() {
        return this.eme;
    }

    public byte cpD() {
        return this.emf;
    }

    public int[] cjX() {
        return this.egL;
    }

    public aMW[] cpE() {
        return this.emg;
    }

    public aMX cpF() {
        return this.emh;
    }

    public aMY cpG() {
        return this.emi;
    }

    public aMV[] cpH() {
        return this.emj;
    }

    public void reset() {
        this.o = 0;
        this.elG = 0;
        this.ciZ = 0;
        this.elH = 0;
        this.elI = 0;
        this.ejt = 0;
        this.elJ = null;
        this.elK = 0;
        this.elL = 0;
        this.elM = 0;
        this.elN = 0;
        this.elO = 0;
        this.elP = 0;
        this.elQ = 0;
        this.elR = false;
        this.elS = false;
        this.elT = false;
        this.elU = false;
        this.elV = 0;
        this.elW = 0;
        this.elX = null;
        this.elY = null;
        this.elZ = 0;
        this.ema = 0;
        this.emb = 0;
        this.emc = 0;
        this.emd = 0.0f;
        this.eme = 0.0f;
        this.emf = 0;
        this.egL = null;
        this.emg = null;
        this.emh = null;
        this.emi = null;
        this.emj = null;
    }

    public void a(aqH aqH2) {
        int n;
        this.o = aqH2.bGI();
        this.elG = aqH2.bGG();
        this.ciZ = aqH2.bGI();
        this.elH = aqH2.bGI();
        this.elI = aqH2.bGI();
        this.ejt = aqH2.bGG();
        this.elJ = aqH2.bGO();
        this.elK = aqH2.bGI();
        this.elL = aqH2.bGG();
        this.elM = aqH2.aTf();
        this.elN = aqH2.aTf();
        this.elO = aqH2.aTf();
        this.elP = aqH2.bGI();
        this.elQ = aqH2.bGI();
        this.elR = aqH2.bxv();
        this.elS = aqH2.bxv();
        this.elT = aqH2.bxv();
        this.elU = aqH2.bxv();
        this.elV = aqH2.bGG();
        this.elW = aqH2.aTf();
        this.elX = aqH2.bGL().intern();
        this.elY = aqH2.bGM();
        this.elZ = aqH2.aTf();
        this.ema = aqH2.aTf();
        this.emb = aqH2.aTf();
        this.emc = aqH2.aTf();
        this.emd = aqH2.bGH();
        this.eme = aqH2.bGH();
        this.emf = aqH2.aTf();
        this.egL = aqH2.bGM();
        int n2 = aqH2.bGI();
        this.emg = new aMW[n2];
        for (n = 0; n < n2; ++n) {
            this.emg[n] = new aMW();
            this.emg[n].a(aqH2);
        }
        if (aqH2.aTf() != 0) {
            this.emh = new aMX();
            this.emh.a(aqH2);
        } else {
            this.emh = null;
        }
        if (aqH2.aTf() != 0) {
            this.emi = new aMY();
            this.emi.a(aqH2);
        } else {
            this.emi = null;
        }
        n = aqH2.bGI();
        this.emj = new aMV[n];
        for (int i = 0; i < n; ++i) {
            this.emj[i] = new aMV();
            this.emj[i].a(aqH2);
        }
    }

    public final int bGA() {
        return ewj.oyZ.d();
    }
}
