/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  azl
 *  eNk
 *  eXx
 *  ewu
 *  exP
 *  eyU
 *  ffS
 *  fqG
 *  fqL
 *  fqN
 *  fqO
 *  fqR
 *  fqS
 *  org.apache.log4j.Logger
 */
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import org.apache.log4j.Logger;

public abstract class fqD {
    protected static final Logger sTZ = Logger.getLogger(fqD.class);
    private final int sUa;
    private final short sUb;
    private final int sUc;
    private final byte sUd;
    private final float sUe;
    private final float sUf;
    private final byte sUg;
    private final boolean sUh;
    private final boolean sUi;
    private final boolean sUj;
    private final boolean sUk;
    private final byte sUl;
    private final byte sUm;
    private final short sUn;
    private final byte sUo;
    private final ang sUp;
    private final ang sUq;
    private final int sUr;
    private final ang sUs;
    private final short sUt;
    private final fqN sUu;
    private final Map<ang, fqN> sUv;
    private final azl<eNk> sUw = new azl();
    private EnumSet<fqS> qEr;
    private boolean spr;
    private final byte sUx;
    private final boolean sUy;
    private final boolean sUz;
    private final boolean sUA;
    private final boolean sUB;
    private final boolean sUC;
    private final boolean sUD;
    private final ewu sUE;
    protected final short sUF;

    protected fqD(fqR fqR2) {
        this.sUa = fqR2.d();
        this.sUb = fqR2.aVe();
        this.sUc = fqR2.xT();
        this.sUd = fqR2.gjl();
        this.sUe = fqR2.cvc();
        this.sUf = fqR2.cvd();
        this.sUg = fqR2.eeR();
        this.sUh = fqR2.cvi();
        this.sUj = fqR2.cvl();
        this.sUi = fqR2.cvj();
        this.sUk = fqR2.cvk();
        this.sUr = fqR2.cvm();
        this.sUs = fqR2.giF();
        this.sUt = fqR2.cvo();
        this.sUu = new fqN();
        Map map = fqR2.gjs();
        if (map != null) {
            for (Map.Entry entry : map.entrySet()) {
                this.sUu.a((eXx)entry.getKey(), ((fqG)entry.getValue()).giT(), ((fqG)entry.getValue()).cwh());
            }
        }
        this.sUv = fqR2.gjr();
        this.sUu.bD(fqR2.cvx(), fqR2.cvy());
        this.sUu.bE(fqR2.cvv(), fqR2.gjn());
        this.sUu.nK(fqR2.cvf());
        this.sUu.nL(fqR2.gjm());
        this.sUu.nM(fqR2.cvh());
        this.sUu.nN(fqR2.gjo());
        this.sUu.fh((float)fqR2.eeR());
        this.sUu.fi((float)fqR2.gjl());
        this.sUu.fj(fqR2.cvc());
        this.sUu.fk(fqR2.cvd());
        this.sUu.nO(fqR2.cvi());
        this.sUu.nP(fqR2.cvj());
        this.sUu.nQ(fqR2.cvl());
        this.sUu.nR(fqR2.cvO());
        this.sUm = fqR2.giH();
        this.sUl = fqR2.giG();
        this.sUn = fqR2.cvB();
        this.sUp = fqR2.giI();
        this.sUq = fqR2.giJ();
        this.sUo = fqR2.giK();
        this.sUx = fqR2.cvF();
        this.sUy = fqR2.cvP();
        this.sUz = fqR2.cvI();
        this.sUA = fqR2.cvL();
        this.spr = false;
        this.sUB = fqR2.cvM();
        this.sUC = fqR2.cvN();
        this.sUD = fqR2.cvO();
        this.sUE = fqR2.giO();
        this.sUF = fqR2.cvD();
        this.U(fqR2.ckm());
    }

    public int d() {
        return this.sUa;
    }

    public void v(eNk eNk2) {
        this.sUw.M((Object)eNk2);
        if (eNk2.df(1L)) {
            this.spr = true;
        }
    }

    public Iterator<eNk> fA(short s) {
        return this.fB(s).iterator();
    }

    public ArrayList<eNk> fB(short s) {
        int n = this.sUw.aVo();
        ArrayList<eNk> arrayList = new ArrayList<eNk>(n);
        for (int i = 0; i < n; ++i) {
            eNk eNk2 = (eNk)this.sUw.vK(i);
            if (s < eNk2.fAv() || s > eNk2.fAw()) continue;
            arrayList.add(eNk2);
        }
        return arrayList;
    }

    public boolean fYh() {
        return this.spr;
    }

    public int Fq() {
        return this.sUb;
    }

    public int xT() {
        return this.sUc;
    }

    public short cvo() {
        return this.sUt;
    }

    public byte a(fqE fqE2, exP exP2, Object object, Object object2) {
        fqN fqN2 = this.a(exP2, object, fqE2, object2);
        return (byte)fqN2.cwa();
    }

    public float b(fqE fqE2, exP exP2, Object object, Object object2) {
        fqN fqN2 = this.a(exP2, object, fqE2, object2);
        return (byte)fqN2.cwb();
    }

    public float c(fqE fqE2, exP exP2, Object object, Object object2) {
        fqN fqN2 = this.a(exP2, object, fqE2, object2);
        return (byte)fqN2.cwc();
    }

    public byte d(fqE fqE2, exP exP2, Object object, Object object2) {
        fqN fqN2 = this.a(exP2, object, fqE2, object2);
        return (byte)fqN2.cvZ();
    }

    public boolean a(fqE fqE2, Object object, Object object2, Object object3) {
        fqN fqN2 = this.a(object, object2, fqE2, object3);
        return fqN2.cvV();
    }

    public boolean b(fqE fqE2, Object object, Object object2, Object object3) {
        fqN fqN2 = this.a(object, object2, fqE2, object3);
        return fqN2.cvW();
    }

    public boolean c(fqE fqE2, Object object, Object object2, Object object3) {
        fqN fqN2 = this.a(object, object2, fqE2, object3);
        return fqN2.cvX();
    }

    public boolean d(fqE fqE2, Object object, Object object2, Object object3) {
        fqN fqN2 = this.a(object, object2, fqE2, object3);
        return fqN2.gja();
    }

    public boolean e(fqE fqE2, exP exP2, Object object, Object object2) {
        fqN fqN2 = this.a(exP2, object, fqE2, object2);
        return fqN2.cwf();
    }

    public boolean f(fqE fqE2, exP exP2, Object object, Object object2) {
        fqN fqN2 = this.a(exP2, object, fqE2, object2);
        return fqN2.cwe();
    }

    public boolean fYo() {
        return this.sUk;
    }

    public int cvm() {
        return this.sUr;
    }

    public ang giF() {
        return this.sUs;
    }

    public byte giG() {
        return this.sUl;
    }

    public byte giH() {
        return this.sUm;
    }

    public fqO g(fqE fqE2, exP exP2, Object object, Object object2) {
        fqN fqN2 = this.a(exP2, object, fqE2, object2);
        eyU eyU2 = exP2.fhl();
        fqO fqO2 = new fqO();
        Map map = fqN2.giX();
        Set set = map.keySet();
        short s = fqE2.cmL();
        for (eXx eXx2 : set) {
            fqG fqG2 = (fqG)map.get(eXx2);
            int n = fqG2.Ph((int)s);
            int n2 = 0;
            if (this.qEr != null) {
                for (fqS fqS2 : this.qEr) {
                    n2 += eyU2.a(eXx2, fqS2);
                }
            }
            if (eXx2 == eXx.rHH) {
                fqO2.h(eXx2.aJr(), n + n2);
                continue;
            }
            fqO2.g(eXx2.aJr(), Math.max(0, n + n2));
        }
        return fqO2;
    }

    public int Zc(int n) {
        if (n < 0 || n > this.sUb) {
            throw new IllegalArgumentException("Level invalide : " + n + " demand\u00e9, max=" + this.sUb);
        }
        fqN fqN2 = this.sUu;
        return fqN2.c(eXx.rGj, n);
    }

    public int h(fqE fqE2, exP exP2, Object object, Object object2) {
        if (fqE2 == null) {
            throw new IllegalArgumentException("SpellLevel null");
        }
        short s = fqE2.cmL();
        if (s < 0 || s > this.sUb) {
            throw new IllegalArgumentException("Level invalide : " + s + " demand\u00e9, max=" + this.sUb);
        }
        fqO fqO2 = this.g(fqE2, exP2, object, object2);
        return fqO2.r(eXx.rGj);
    }

    public int Zd(int n) {
        if (n < 0 || n > this.sUb) {
            throw new IllegalArgumentException("Level invalide : " + n + " demand\u00e9, max=" + this.sUb);
        }
        return this.sUu.c(eXx.rGl, n);
    }

    public int e(fqE fqE2, Object object, Object object2, Object object3) {
        if (fqE2 == null) {
            throw new IllegalArgumentException("SpellLevel null");
        }
        short s = fqE2.cmL();
        if (s < 0 || s > this.sUb) {
            throw new IllegalArgumentException("Level invalide : " + String.valueOf(fqE2) + " demand\u00e9, max=" + this.sUb);
        }
        fqN fqN2 = this.y(object, object2, fqE2, object3);
        return fqN2.c(eXx.rGl, (int)s);
    }

    public int Ze(int n) {
        if (n < 0 || n > this.sUb) {
            throw new IllegalArgumentException("Level invalide : " + n + " demand\u00e9, max=" + this.sUb);
        }
        return this.sUu.c(eXx.rHT, n);
    }

    public int f(fqE fqE2, Object object, Object object2, Object object3) {
        if (fqE2 == null) {
            throw new IllegalArgumentException("SpellLevel null");
        }
        short s = fqE2.cmL();
        if (s < 0 || s > this.sUb) {
            throw new IllegalArgumentException("Level invalide : " + String.valueOf(fqE2) + " demand\u00e9, max=" + this.sUb);
        }
        fqN fqN2 = this.y(object, object2, fqE2, object3);
        return fqN2.c(eXx.rHT, (int)s);
    }

    public int Zf(int n) {
        if (n < 0 || n > this.sUb) {
            throw new IllegalArgumentException("Level invalide : " + n + " demand\u00e9, max=" + this.sUb);
        }
        return this.sUu.c(eXx.rGk, n);
    }

    public int g(fqE fqE2, Object object, Object object2, Object object3) {
        fqN fqN2 = this.a(object, object2, fqE2, object3);
        short s = fqE2.cmL();
        return fqN2.c(eXx.rGk, (int)s);
    }

    public int Zg(int n) {
        if (n < 0 || n > this.sUb) {
            throw new IllegalArgumentException("Level invalide : " + n + " demand\u00e9, max=" + this.sUb);
        }
        return this.sUu.giZ().Ph(n);
    }

    public int i(fqE fqE2, exP exP2, Object object, Object object2) {
        fqN fqN2 = this.a(exP2, object, fqE2, object2);
        short s = fqE2.cmL();
        int n = fqN2.giZ().Ph((int)s);
        eyU eyU2 = exP2.fhl();
        int n2 = 0;
        if (this.qEr != null) {
            for (fqS fqS2 : this.qEr) {
                n2 += eyU2.b(fqS2);
            }
        }
        return n + n2;
    }

    public int j(fqE fqE2, exP exP2, Object object, Object object2) {
        fqN fqN2 = this.a(exP2, object, fqE2, object2);
        short s = fqE2.cmL();
        return fqN2.giY().Ph((int)s);
    }

    public short cvB() {
        return this.sUn;
    }

    public ang giI() {
        return this.sUp;
    }

    public ang giJ() {
        return this.sUq;
    }

    public byte giK() {
        return this.sUo;
    }

    public boolean eeY() {
        return this.sUx != fqL.sVB.aJr();
    }

    public boolean giL() {
        return this.sUx == fqL.sVD.aJr();
    }

    public boolean cvP() {
        return this.sUy;
    }

    public byte giM() {
        return ffS.sgQ.aJr();
    }

    public boolean giN() {
        return this.sUz;
    }

    public boolean cvL() {
        return this.sUA;
    }

    public boolean k(fqE fqE2, exP exP2, Object object, Object object2) {
        fqN fqN2 = this.a(exP2, object, fqE2, object2);
        return fqN2.cwd();
    }

    public boolean cvM() {
        return this.sUB;
    }

    public boolean cvN() {
        return this.sUC;
    }

    public boolean l(fqE fqE2, exP exP2, Object object, Object object2) {
        fqN fqN2 = this.a(exP2, object, fqE2, object2);
        return fqN2.cvO();
    }

    public ewu giO() {
        return this.sUE;
    }

    public short cvD() {
        return this.sUF;
    }

    public final void U(int ... nArray) {
        if (nArray == null) {
            return;
        }
        for (int i = 0; i < nArray.length; ++i) {
            int n = nArray[i];
            fqS fqS2 = fqS.Zk((int)n);
            this.f(fqS2);
        }
    }

    public final void f(fqS fqS2) {
        if (fqS2 == null) {
            return;
        }
        if (this.qEr == null) {
            this.qEr = EnumSet.noneOf(fqS.class);
        }
        this.qEr.add(fqS2);
    }

    public final boolean g(fqS fqS2) {
        if (this.qEr == null) {
            return false;
        }
        return this.qEr.contains(fqS2);
    }

    private fqN a(Object object, Object object2, fqE fqE2, Object object3) {
        if (fqE2 == null) {
            throw new IllegalArgumentException("SpellLevel null");
        }
        short s = fqE2.cmL();
        if (s < 0 || s > this.sUb) {
            throw new IllegalArgumentException("Level invalide : " + s + " demand\u00e9, max=" + this.sUb);
        }
        return this.y(object, object2, fqE2, object3);
    }

    private fqN y(Object object, Object object2, Object object3, Object object4) {
        fqN fqN2 = this.sUu;
        if (this.sUv != null && !this.sUv.isEmpty()) {
            Set<ang> set = this.sUv.keySet();
            for (ang ang2 : set) {
                if (!ang2.b(object, object2, object3, object4)) continue;
                fqN2 = this.sUv.get(ang2);
            }
        }
        return fqN2;
    }
}
